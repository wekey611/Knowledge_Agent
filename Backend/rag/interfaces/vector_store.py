# rag/interfaces/vector_store.py
"""
向量存储接口定义。

为什么需要这个接口：
    向量库有多种实现（Chroma、FAISS、Pinecone、Milvus 等），
    业务代码不应该知道具体用了哪个。定义接口后，业务代码依赖此接口，
    换向量库只改 factory.py，不动业务代码。

依赖倒置原则（DIP）：
    高层模块（业务代码）不依赖低层模块（具体向量库），
    两者都依赖抽象（本接口）。

修复历史：
    V0.1（首次版）依赖了 langchain_core.documents.Document，导致接口和 LangChain 强绑定。
    V0.2（当前版）定义自己的 Chunk 数据结构，接口层不再 import 任何外部库。
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple


@dataclass
class Chunk:
    """
    向量库存储的最小数据单元。

    为什么自己定义 Chunk（而不是用 LangChain 的 Document）：
        1. 接口层零外部依赖：langchain_core 不是 rag 模块必须装的依赖
        2. 实现层自由：Chroma 实现可以用 langchain_chroma 包装，FAISS 实现可以裸用，
           两者都对外暴露 Chunk，业务代码无感
        3. 测试友好：测试时不用 import LangChain 也能 mock

    Attributes:
        id: 向量库内部唯一 ID（add 时由实现类生成或外部传入）
        content: 原文内容（用于拼 Prompt 给 LLM）
        embedding: 向量表示（add 时必填，search 返回时可空）
        metadata: 元数据（kb_id、doc_id、source_file、chunk_index 等过滤/溯源用）
        score: 检索时的相似度分数（add 时为空）
    """

    id: str = ""
    content: str = ""
    embedding: Optional[List[float]] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    score: Optional[float] = None


class VectorStoreInterface(ABC):
    """
    向量存储抽象接口。

    所有向量库实现（Chroma、FAISS、Pinecone、Milvus、InMemory 等）都必须继承此类。

    设计原则：接口最小完备
        - 核心方法（@abstractmethod）：所有实现必须支持
        - 扩展方法（带默认实现）：部分实现支持，不支持时抛 NotImplementedError
        这样不同成熟度的实现类可以共存，不被强制实现它们不支持的能力。

    为什么 search 接收 query_embedding 而不是 query 字符串：
        向量库只能做向量相似度计算。"字符串 → 向量"是 Embedding 的工作，
        不是 VectorStore 的工作。让接口接收字符串会把 Embedding 偷偷塞进
        VectorStore 的实现里，破坏分层。
        Retriever 负责：先调 Embedding 拿到向量，再调 VectorStore.search。
    """

    # ==================== 核心方法（必须实现） ====================

    @abstractmethod
    def add(self, chunks: List[Chunk]) -> List[str]:
        """
        添加 chunks 到向量库。

        Args:
            chunks: 待添加的 Chunk 列表，每个必须包含 content + embedding + metadata
                    （embedding 可由本方法内部计算，但接口约定 caller 传 embedding）

        Returns:
            添加成功的 chunk ID 列表（顺序与输入一致）

        Raises:
            ValueError: 当 chunks 为空或字段缺失时
            StorageError: 当底层向量库写入失败时

        Note:
            实现要点：
            - 输入 chunks 的 embedding 字段必须已填充（接口约定）
            - 内部按 metadata[kb_id] 做 collection/namespace 隔离
            - 返回 ID 列表方便上层记录映射关系
        """
        raise NotImplementedError

    @abstractmethod
    def search(
        self,
        query_embedding: List[float],
        top_k: int = 5,
        filter: Optional[Dict[str, Any]] = None,
    ) -> List[Chunk]:
        """
        根据查询向量检索最相关的 chunks。

        Args:
            query_embedding: 查询的向量表示（由 Embedding 模型生成）
            top_k: 返回的 chunk 数量
            filter: 元数据过滤条件，例如 {"kb_id": 1, "doc_id": 123}

        Returns:
            按相似度降序排列的 Chunk 列表（包含 score 字段）

        Raises:
            ValueError: 当 query_embedding 维度不匹配索引维度时
            StorageError: 当底层查询失败时

        Note:
            实现要点：
            - 必须支持 metadata 过滤（kb_id 隔离是基础需求）
            - 返回的 Chunk 必须填充 score 字段（除非实现类选择抛错表示不支持）
        """
        raise NotImplementedError

    @abstractmethod
    def delete_by_doc_id(self, doc_id: int) -> int:
        """
        根据文档 ID 删除该文档的所有 chunks。

        Args:
            doc_id: 业务文档 ID（来自你项目 Document 表的主键）

        Returns:
            删除的 chunk 数量

        Raises:
            StorageError: 当底层删除失败时

        Note:
            业务场景：你的项目里删除文档时调用此方法，清理向量库中
            该文档的所有 chunks。和 parser_status 状态机配合：
            文档删除 → 此方法清理向量库 → 物理文件清理。
        """
        raise NotImplementedError

    # ==================== 扩展方法（可选，默认抛错） ====================

    def delete_all(self) -> int:
        """
        清空向量库中的所有数据。

        Warning:
            不可逆操作，主要用于测试。生产环境慎用。
        """
        raise NotImplementedError("当前实现不支持 delete_all")

    def count(self) -> int:
        """
        返回向量库中的 chunk 总数。
        """
        raise NotImplementedError("当前实现不支持 count")

    def search_with_score(
        self,
        query_embedding: List[float],
        top_k: int = 5,
        filter: Optional[Dict[str, Any]] = None,
    ) -> List[Tuple[Chunk, float]]:
        """
        检索并返回 (chunk, score) 元组。

        默认实现：调用 search 方法，从 chunk.score 提取分数。
        部分实现（如 Chroma）可以重写以直接返回元组，避免一次额外转换。
        """
        chunks = self.search(query_embedding, top_k, filter)
        return [(c, c.score or 0.0) for c in chunks]

    def persist(self) -> None:
        """
        显式持久化到磁盘。

        Note:
            - Chroma 自动持久化，可不重写
            - FAISS 必须显式调用保存
            - InMemory 实现调用此方法应抛错
        """
        raise NotImplementedError("当前实现无需 persist（自动持久化或不支持）")