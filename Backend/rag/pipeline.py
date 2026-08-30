"""
RAGPipeline：完整 RAG 流程的对外入口。

query → Retriever.retrieve() → chunks → Generator.generate() → answer

V3: 完整实现。
V5 扩展：加混合检索、Rerank 等。
"""
from dataclasses import dataclass
from typing import List

from rag.generator import Generator
from rag.interfaces.vector_store import Chunk
from rag.retriever import Retriever


@dataclass
class RAGResponse:
    """
    RAG 回答结果。

    Attributes:
        answer: 生成的答案
        sources: 引用的 chunk 列表（含 source_file）
        query: 原始查询（方便前端回显）
    """

    answer: str
    sources: List[dict]
    query: str

    def to_dict(self) -> dict:
        return {
            "answer": self.answer,
            "sources": self.sources,
            "query": self.query,
        }


class RAGPipeline:
    """
    完整 RAG 流程。

    Attributes:
        retriever: 检索器
        generator: 生成器
    """

    def __init__(self, retriever: Retriever, generator: Generator):
        self.retriever = retriever
        self.generator = generator

    async def query(
        self,
        query: str,
        kb_id: int,
        top_k: int = None,
    ) -> RAGResponse:
        """
        执行 RAG 查询。

        Args:
            query: 用户问题
            kb_id: 知识库 ID
            top_k: 检索数量（None 用 Retriever 默认值）

        Returns:
            RAGResponse 含答案 + 引用来源
        """
        # 1. 检索
        chunks = await self.retriever.retrieve(
            query=query,
            kb_id=kb_id,
            top_k=top_k,
        )

        # 2. 生成答案
        answer = await self.generator.generate(query=query, chunks=chunks)

        # 3. 构造引用来源
        sources = []
        for chunk in chunks:
            sources.append({
                "chunk_id": chunk.id,
                "score": round(chunk.score, 4) if chunk.score else None,
                "source_file": chunk.metadata.get("source_file", "未知"),
                "preview": chunk.content[:100],
            })

        return RAGResponse(
            answer=answer,
            sources=sources,
            query=query,
        )


__all__ = ["RAGPipeline", "RAGResponse"]