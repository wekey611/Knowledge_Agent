"""
Retriever：封装"检索"逻辑。

V2: Retriever（纯向量检索）
V5: 加 HybridRetriever（向量 + BM25）

依赖：
    纯标准库 + rag 内置组件，零外部依赖（BM25Retriever 单独需要 rank_bm25）
"""
from typing import List, Optional

from rag.implementations.bm25 import BM25Retriever
from rag.interfaces.embedding import EmbeddingInterface
from rag.interfaces.vector_store import Chunk, VectorStoreInterface


class Retriever:
    """
    检索器（V2）：把用户 query 转为相关 chunks。

    Attributes:
        embedding: Embedding 模型
        vector_store: 向量库
        default_top_k: 默认返回的 chunk 数量
    """

    def __init__(
        self,
        embedding: EmbeddingInterface,
        vector_store: VectorStoreInterface,
        default_top_k: int = 5,
    ):
        self.embedding = embedding
        self.vector_store = vector_store
        self.default_top_k = default_top_k

    async def retrieve(
        self,
        query: str,
        kb_id: int,
        top_k: Optional[int] = None,
        filter: Optional[dict] = None,
    ) -> List[Chunk]:
        """检索与 query 相关的 chunks（纯向量）。"""
        query_embedding = await self.embedding.embed_query(query)
        final_filter = {"kb_id": kb_id}
        if filter:
            final_filter.update(filter)
        return self.vector_store.search(
            query_embedding=query_embedding,
            top_k=top_k or self.default_top_k,
            filter=final_filter,
        )


class HybridRetriever:
    """
    混合检索器（V5）：向量 + BM25 + RRF 融合。

    为什么需要混合检索：
        - 向量检索擅长"语义相似"
        - BM25 擅长"精确关键词"
        - 混合能提升召回率（特别是专业术语/缩写场景）

    限制：
        - BM25 需把全部文档加载到内存
        - 适合中等规模（几万 chunks）
        - 大规模需要用 Elasticsearch 等独立 BM25 服务
    """

    def __init__(
        self,
        embedding: EmbeddingInterface,
        vector_store: VectorStoreInterface,
        bm25: BM25Retriever,
        rrf_k: int = 60,
    ):
        self.embedding = embedding
        self.vector_store = vector_store
        self.bm25 = bm25
        self.rrf_k = rrf_k

    @classmethod
    def from_chunks(
        cls,
        embedding: EmbeddingInterface,
        vector_store: VectorStoreInterface,
        chunks: List[Chunk],
        rrf_k: int = 60,
    ):
        """从 chunks 构造（用于已经加载到内存的场景）。"""
        documents = [c.content for c in chunks]
        bm25 = BM25Retriever(documents)
        return cls(embedding, vector_store, bm25, rrf_k)

    async def retrieve(
        self,
        query: str,
        kb_id: int,
        top_k: int = 5,
    ) -> List[Chunk]:
        """
        混合检索：向量 + BM25 + RRF 融合。

        V5 简化：先向量检索拿候选，BM25 做关键词加权评分。
        """
        # 1. 向量检索（多取一些）
        query_embedding = await self.embedding.embed_query(query)
        vector_chunks = self.vector_store.search(
            query_embedding=query_embedding,
            top_k=top_k * 2,
            filter={"kb_id": kb_id},
        )

        # 2. 用 BM25 给 vector_chunks 重新打分
        tokenized_query = list(query.replace(" ", "").replace("\n", ""))
        bm25_scores = self.bm25.bm25.get_scores(tokenized_query)

        # 3. 重新计算综合分（向量分 + BM25 分加权）
        scored_chunks = []
        for chunk in vector_chunks:
            # 找到 chunk 对应的 bm25 分数（按内容匹配索引）
            try:
                bm25_idx = self.bm25.tokenized_docs.index(
                    list(chunk.content.replace(" ", "").replace("\n", ""))
                )
                bm25_score = bm25_scores[bm25_idx]
            except ValueError:
                bm25_score = 0.0

            # 综合分 = 向量分 + BM25 分（简单相加）
            combined_score = (chunk.score or 0) + bm25_score * 0.1
            chunk.score = combined_score
            scored_chunks.append(chunk)

        # 4. 按综合分排序
        scored_chunks.sort(key=lambda c: c.score, reverse=True)
        return scored_chunks[:top_k]


__all__ = ["Retriever", "HybridRetriever"]