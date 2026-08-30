"""
索引器（Indexer）：把文档变成可检索的向量数据。

职责编排：
    1. Parser：解析文档为纯文本
    2. Chunker：切分文本为 chunks
    3. Embedding：向量化 chunks
    4. VectorStore：写入向量库

Index 不做具体工作，只串联 4 个组件。
每个组件出错都包装成 IndexingError 抛出。
"""
from pathlib import Path
from typing import List, Optional, Union

from rag.chunker import RecursiveChunker
from rag.exceptions import IndexingError
from rag.implementations.parsers import TextParser, MarkdownParser, PDFParser
from rag.interfaces.embedding import EmbeddingInterface
from rag.interfaces.parser import DocumentParserInterface
from rag.interfaces.vector_store import Chunk, VectorStoreInterface


class Indexer:
    """
    索引编排器。

    Attributes:
        parser: 单个 parser（如果只想支持一种格式）
        parsers: parser 列表（支持多格式自动选择）
        chunker: 切块器
        embedding: embedding 模型
        vector_store: 向量库
    """

    def __init__(
        self,
        embedding: EmbeddingInterface,
        vector_store: VectorStoreInterface,
        chunker: Optional[RecursiveChunker] = None,
        parser: Optional[DocumentParserInterface] = None,
        parsers: Optional[List[DocumentParserInterface]] = None,
    ):
        # 优先级：parsers > parser > 默认
        if parsers is not None:
            self.parsers = parsers
        elif parser is not None:
            self.parsers = [parser]
        else:
            # 默认支持 Markdown + Text（PDF 留 V2）
            self.parsers = [MarkdownParser(), TextParser(), PDFParser()]

        self.chunker = chunker or RecursiveChunker(chunk_size=500, chunk_overlap=50)
        self.embedding = embedding
        self.vector_store = vector_store

    def _select_parser(self, file_path: Union[str, Path]) -> DocumentParserInterface:
        """根据文件后缀选择 parser。"""
        ext = Path(file_path).suffix.lstrip(".").lower()

        for parser in self.parsers:
            if parser.supports_format(ext):
                return parser

        supported = ", ".join(
            f for p in self.parsers for f in p.supported_formats
        )
        raise IndexingError(
            f"不支持的文件格式: .{ext}。当前支持: {supported}"
        )

    async def index_file(
        self,
        file_path: Union[str, Path],
        doc_id: int,
        kb_id: int,
    ) -> List[str]:
        """
        索引一个文件。

        Args:
            file_path: 文件路径
            doc_id: 文档 ID（你的项目 Document 表主键）
            kb_id: 知识库 ID

        Returns:
            写入向量库的 chunk ID 列表

        Raises:
            IndexingError: 索引任何阶段失败
        """
        file_path = Path(file_path)
        if not file_path.exists():
            raise IndexingError(f"文件不存在: {file_path}")

        # 1. 选 parser
        parser = self._select_parser(file_path)

        # 2. 解析
        try:
            parsed = parser.parse(file_path)
        except Exception as e:
            raise IndexingError(f"文档解析失败 ({file_path}): {e}") from e

        if not parsed.content.strip():
            raise IndexingError(f"文档内容为空: {file_path}")

        # 3. 切块
        try:
            chunks = self.chunker.split(
                parsed.content,
                doc_id=doc_id,
                kb_id=kb_id,
                source_file=file_path.name,
            )
        except Exception as e:
            raise IndexingError(f"切块失败: {e}") from e

        if not chunks:
            raise IndexingError(f"切块后无内容: {file_path}")

        # 4. embedding
        try:
            texts = [c.content for c in chunks]
            embeddings = await self.embedding.embed_documents(texts)
        except Exception as e:
            raise IndexingError(f"Embedding 失败: {e}") from e

        if len(embeddings) != len(chunks):
            raise IndexingError(
                f"Embedding 数量不匹配: 期望 {len(chunks)}, 实际 {len(embeddings)}"
            )

        # 把 embedding 填回 chunks
        for chunk, vec in zip(chunks, embeddings):
            chunk.embedding = vec

        # 5. 写入向量库
        try:
            ids = self.vector_store.add(chunks)
        except Exception as e:
            raise IndexingError(f"写入向量库失败: {e}") from e

        return ids


__all__ = ["Indexer"]