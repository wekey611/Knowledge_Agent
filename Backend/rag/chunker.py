"""
递归切块器（Recursive Character Text Splitter）。

为什么需要切块：
    1. Embedding 模型有输入长度限制（BGE-M3 = 8192 token）
    2. 向量检索的精度：500 token 的块比 5000 token 检索更准
    3. LLM 拼 prompt 时 chunks 不能太长（成本+注意力）

为什么用递归切块：
    按优先级尝试切分点，先按段落，再按句子，再按逗号，最后按字符。
    语义边界优先，避免切断完整句子。

依赖：
    纯标准库，零外部依赖。

参考：
    LangChain RecursiveCharacterTextSplitter 的核心算法，
    但自己实现保持 rag/ 模块零外部依赖。
"""
from typing import List, Optional

from dataclasses import dataclass, field
from typing import Any, Dict

from rag.interfaces.vector_store import Chunk


@dataclass
class ChunkMetadata:
    """
    Chunk 的元数据（持久化到向量库的 metadata 字段）。

    Attributes:
        doc_id: 文档 ID（来自你项目 Document 表的主键）
        kb_id: 知识库 ID
        chunk_index: 当前 chunk 在文档内的序号（从 0 开始）
        start_char: chunk 在原文中的起始字符位置（用于溯源）
        end_char: chunk 在原文中的结束字符位置
        source_file: 源文件名（可选，便于前端展示）
    """

    doc_id: int
    kb_id: int
    chunk_index: int
    start_char: int = 0
    end_char: int = 0
    source_file: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """转成 Chroma metadata 接受的 dict（去除 None 值）。"""
        d = {
            "doc_id": self.doc_id,
            "kb_id": self.kb_id,
            "chunk_index": self.chunk_index,
            "start_char": self.start_char,
            "end_char": self.end_char,
        }
        if self.source_file is not None:
            d["source_file"] = self.source_file
        return d


class RecursiveChunker:
    """
    递归切块器。

    Attributes:
        chunk_size: 单 chunk 最大字符数（推荐 300~800）
        chunk_overlap: 相邻 chunk 重叠字符数（推荐 chunk_size 的 10%~20%）
        separators: 分隔符优先级列表（从前到后尝试）
        length_function: 长度计算函数（默认 len()，可换成按 token 数计算）

    Note:
        V1 用字符数（len()），简单但不够精确。
        V2 优化版：用 tokenizer 算 token 数（BGE-M3 按 token 切更准）。
    """

    DEFAULT_SEPARATORS = [
        "\n\n",  # 1. 段落（最强语义边界）
        "\n",    # 2. 行/标题
        "。",    # 3. 中文句号
        "！",    # 4. 中文感叹号
        "？",    # 5. 中文问号
        "；",    # 6. 中文分号
        "，",    # 7. 中文逗号
        " ",     # 8. 空格（兜底）
        "",      # 9. 强制按字符切（最终兜底）
    ]

    def __init__(
        self,
        chunk_size: int = 500,
        chunk_overlap: int = 50,
        separators: Optional[List[str]] = None,
    ):
        if chunk_overlap >= chunk_size:
            raise ValueError(
                f"chunk_overlap ({chunk_overlap}) 必须小于 chunk_size ({chunk_size})"
            )
        if chunk_size <= 0:
            raise ValueError(f"chunk_size 必须大于 0，当前: {chunk_size}")

        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.separators = separators or self.DEFAULT_SEPARATORS

    # ==================== 主入口 ====================

    def split(
        self,
        text: str,
        doc_id: int,
        kb_id: int,
        source_file: Optional[str] = None,
    ) -> List[Chunk]:
        """
        把文本切成 List[Chunk]。

        Args:
            text: 原始文本
            doc_id: 文档 ID（用于 metadata）
            kb_id: 知识库 ID（用于 metadata）
            source_file: 源文件名（可选，用于 metadata）

        Returns:
            List[Chunk]，每个 Chunk 含 content 和 metadata（doc_id/kb_id/chunk_index/start_char/end_char）

        Example:
            >>> chunker = RecursiveChunker(chunk_size=500, chunk_overlap=50)
            >>> chunks = chunker.split("长文本...", doc_id=1, kb_id=1)
            >>> len(chunks)
            12
        """
        if not text or not text.strip():
            return []

        # 递归切分，得到 (text, start_char) 元组列表
        # 关键：保留每个 chunk 在原文中的位置，用于溯源
        text_chunks = self._split_text_with_positions(text, self.separators)

        # 包装成 Chunk 对象
        chunks: List[Chunk] = []
        for index, (chunk_text, start_char) in enumerate(text_chunks):
            metadata = ChunkMetadata(
                doc_id=doc_id,
                kb_id=kb_id,
                chunk_index=index,
                start_char=start_char,
                end_char=start_char + len(chunk_text),
                source_file=source_file,
            ).to_dict()

            chunks.append(
                Chunk(
                    id=f"{doc_id}_{index}",  # 默认 ID：doc_chunk_index
                    content=chunk_text,
                    metadata=metadata,
                )
            )

        return chunks

    # ==================== 核心递归逻辑 ====================

    def _split_text_with_positions(
        self,
        text: str,
        separators: List[str],
        base_offset: int = 0,
    ) -> List[tuple[str, int]]:
        """
        递归切分文本，返回 (chunk_text, start_char) 列表。

        Args:
            text: 待切分文本
            separators: 当前可用的分隔符列表（递归时会缩小）
            base_offset: 文本在原文中的起始偏移（用于递归时累计位置）

        Returns:
            [(chunk_text, start_char), ...]
        """
        # 终止条件 1：文本足够短，直接返回
        if len(text) <= self.chunk_size:
            return [(text, base_offset)]

        # 终止条件 2：没有分隔符可用，按字符硬切
        if not separators:
            return self._hard_split(text, base_offset)

        # 取当前最强分隔符
        separator = separators[0]
        remaining_separators = separators[1:]

        # 用 separator 切分
        if separator:
            pieces = text.split(separator)
        else:
            pieces = [text]

        # 合并 pieces 成不超过 chunk_size 的 chunks
        return self._merge_pieces(
            pieces, separator, remaining_separators, base_offset
        )

    def _merge_pieces(
        self,
        pieces: List[str],
        separator: str,
        remaining_separators: List[str],
        base_offset: int,
    ) -> List[tuple[str, int]]:
        """
        把 pieces 合并成不超过 chunk_size 的 chunks。

        算法：
            1. 逐个累加 pieces，累加到接近 chunk_size 时停止
            2. 把这段累加的文本合并成一个 chunk
            3. 下一个 chunk 从当前 chunk 末尾往前回退 chunk_overlap 字符开始（实现 overlap）
            4. 处理剩余 pieces 和当前 piece 的尾巴（递归调用）
        """
        chunks = []
        current_chunk: List[str] = []
        current_length = 0
        current_offset = base_offset  # 当前 chunk 在原文中的起始位置
        separator_len = len(separator) if separator else 0

        # 累计到当前 piece 之前的所有 pieces 总长度
        # （按需计算，因为 piece 在循环开始前未定义）
        offset_before_piece = 0

        for piece in pieces:
            piece_length = len(piece)

            # 如果单个 piece 就超过 chunk_size，需要递归切这个 piece
            if piece_length > self.chunk_size:
                # 先把 current_chunk 收尾
                if current_chunk:
                    merged = self._join_pieces(current_chunk, separator)
                    chunks.append((merged, current_offset))
                    # overlap 之后,offset = 刚 append 的 merged 末尾 - overlap
                    if self.chunk_overlap > 0 and len(merged) > self.chunk_overlap:
                        current_offset = chunks[-1][1] + len(merged) - self.chunk_overlap
                    else:
                        current_offset = chunks[-1][1] + len(merged)

                # 递归切这个超长 piece
                # 它的 offset = base_offset + 之前累计的所有 pieces 长度
                piece_offset = base_offset + offset_before_piece
                sub_chunks = self._split_text_with_positions(
                    piece, remaining_separators, piece_offset
                )
                chunks.extend(sub_chunks)

                # 后续 piece 的 offset 应接着最后一个 sub_chunk 的结尾
                if sub_chunks:
                    last_sub_text, last_sub_start = sub_chunks[-1]
                    current_offset = last_sub_start + len(last_sub_text)
                else:
                    current_offset = base_offset + offset_before_piece + len(piece)
                current_chunk = []
                current_length = 0
                offset_before_piece += len(piece) + separator_len
                continue

            # 累加 piece 到 current_chunk
            # 如果累加后超过 chunk_size，收尾 + 开新 chunk
            if current_length + piece_length + separator_len > self.chunk_size:
                # 收尾当前 chunk
                merged = self._join_pieces(current_chunk, separator)
                chunks.append((merged, current_offset))

                # overlap 处理
                current_chunk, current_length, _ = self._apply_overlap(
                    merged, separator
                )
                # 下一个 chunk 的起始 offset = 刚收尾 chunk 末尾 - overlap
                if self.chunk_overlap > 0 and len(merged) > self.chunk_overlap:
                    current_offset = chunks[-1][1] + len(merged) - self.chunk_overlap
                else:
                    current_offset = chunks[-1][1] + len(merged)

            current_chunk.append(piece)
            current_length += piece_length + separator_len
            offset_before_piece += len(piece) + separator_len

        # 收尾最后一段
        if current_chunk:
            merged = self._join_pieces(current_chunk, separator)
            if merged.strip():  # 跳过纯空白
                chunks.append((merged, current_offset))

        return chunks

    def _apply_overlap(
        self,
        last_chunk_text: str,
        separator: str,
    ) -> tuple[List[str], int, int]:
        """
        计算下一个 chunk 的 overlap 起点。

        Returns:
            (carry_over_pieces, carry_length, new_offset)
        """
        if self.chunk_overlap <= 0 or len(last_chunk_text) <= self.chunk_overlap:
            return [], 0, 0

        # 取最后 chunk_overlap 个字符作为 overlap
        overlap_text = last_chunk_text[-self.chunk_overlap:]
        # 把 overlap 文本作为下一个 chunk 的起始 piece
        return [overlap_text], len(overlap_text), 0  # offset 在调用方修正

    def _join_pieces(self, pieces: List[str], separator: str) -> str:
        """用 separator 把 pieces 合并成一个字符串。"""
        if not pieces:
            return ""
        if not separator:
            return "".join(pieces)
        return separator.join(pieces)

    def _hard_split(self, text: str, base_offset: int) -> List[tuple[str, int]]:
        """最终兜底：按字符数硬切。"""
        chunks = []
        step = self.chunk_size - self.chunk_overlap
        for i in range(0, len(text), step):
            chunk_text = text[i:i + self.chunk_size]
            chunks.append((chunk_text, base_offset + i))
        return chunks


def text_segment_before(pieces, target_piece, separator):
    """辅助函数：计算 target_piece 之前所有 pieces 的总长度。"""
    total = 0
    for p in pieces:
        if p is target_piece:
            break
        total += len(p) + len(separator)
    return total


__all__ = ["RecursiveChunker", "ChunkMetadata"]