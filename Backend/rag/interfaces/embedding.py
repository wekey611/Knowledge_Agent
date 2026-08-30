# rag/interfaces/embedding.py
"""
Embedding 接口定义。

为什么需要这个接口：
    Embedding 模型有多种实现（BGE-M3 本地、OpenAI API、阿里云 API...），
    业务代码不应该知道具体用了哪个模型。定义接口后，业务代码依赖此接口，
    换模型只改 factory.py，不动业务代码。

"""
from abc import ABC, abstractmethod
from typing import List, Optional


class EmbeddingInterface(ABC):
    """
    Embedding 模型抽象接口。

    所有 embedding 实现都必须继承此类并实现以下方法。

    为什么区分 embed_documents 和 embed_query：
        某些模型对"文档"和"查询"使用不同的编码策略（例如 BGE 的 query 前缀），
        分开两个方法允许实现层做这种优化。
    """

    @abstractmethod
    async def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """
        批量向量化文档列表。

        Args:
            texts: 文档文本列表

        Returns:
            向量列表，每个向量是一个 float 列表

        Note:
            返回顺序与输入顺序一致：result[i] 对应 texts[i] 的向量

        Raises:
            ValueError: 当 texts 为空时
            APIError: 当 API 调用失败时

        Implementation Notes:
            - 应该支持批量调用（一次传多个文本，减少 API 调用次数）
            - 空列表应该返回空列表（不报错）
            - 失败时抛出异常，由调用方决定如何处理
        """
        raise NotImplementedError

    @abstractmethod
    async def embed_query(self, text: str) -> List[float]:
        """
        向量化单个查询。

        Args:
            text: 用户查询文本

        Returns:
            一个 float 列表，表示查询的向量

        Implementation Notes:
            - 单文本场景，调用方不用包成列表
            - 与 embed_documents 实现可能不同（query 前缀等优化）
        """
        raise NotImplementedError

    @property
    @abstractmethod
    def dim(self) -> int:
        """
        返回向量的维度。

        例如 BGE-M3 是 1024 维，OpenAI text-embedding-3-small 是 1536 维。
        向量库的索引必须用对应的维度，否则会报错。
        """
        raise NotImplementedError

    # 可选：添加同步方法的默认实现
    def embed_documents_sync(self, texts: List[str]) -> List[List[float]]:
        """
        同步版本的 embed_documents（可选实现）。

        如果子类没有实现，会抛出 NotImplementedError。
        """
        raise NotImplementedError("同步方法未实现，请使用异步方法或子类实现")

    def embed_query_sync(self, text: str) -> List[float]:
        """
        同步版本的 embed_query（可选实现）。
        """
        raise NotImplementedError("同步方法未实现，请使用异步方法或子类实现")