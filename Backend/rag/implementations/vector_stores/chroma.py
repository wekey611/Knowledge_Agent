"""
Chroma 向量库实现（V2 增强版）。

V2 新增：
    - 单 collection 策略（推荐）：所有 kb 共享一个 collection
    - 多 collection 策略（V1 兼容）：每 kb 一个 collection

V1 单 collection 的问题：
    - 1000+ kb 时启动慢（要加载所有 collection 的 HNSW 索引）
    - 删除需要遍历所有 collection

V2 single_collection 的优点：
    - 启动只加载一个 collection 的索引
    - 删除一次 where 查询搞定
    - 内存占用小

V2 single_collection 的 ID 设计：
    格式：f"kb_{kb_id}_doc_{doc_id}_chunk_{chunk_index}"
    示例："kb_1_doc_5_chunk_3" 表示 kb_id=1, doc_id=5 的第 4 个 chunk
    这样不同 kb 相同 doc_id 也不会冲突。

依赖：
    pip install chromadb
"""
import os
from typing import Any, Dict, List, Optional

import chromadb
from chromadb.config import Settings

from rag.interfaces.vector_store import Chunk, VectorStoreInterface
from rag.exceptions import RetrievalError


class ChromaVectorStore(VectorStoreInterface):
    """
    Chroma 向量库实现。

    Attributes:
        persist_dir: 数据持久化目录
        distance_function: 距离函数（cosine / l2 / ip）
        strategy: 多租户策略
            - "single_collection"（V2 推荐）：所有 kb 共享一个 collection
            - "multi_collection"（V1 兼容）：每 kb 一个 collection
    """

    DISTANCE_FUNCTIONS = ("cosine", "l2", "ip")
    STRATEGIES = ("single_collection", "multi_collection")
    SINGLE_COLLECTION_NAME = "all_chunks"

    def __init__(
        self,
        persist_dir: str = "./chroma_data",
        distance_function: str = "cosine",
        strategy: str = "single_collection",
    ):
        if distance_function not in self.DISTANCE_FUNCTIONS:
            raise ValueError(
                f"distance_function 必须是 {self.DISTANCE_FUNCTIONS} 之一"
            )
        if strategy not in self.STRATEGIES:
            raise ValueError(f"strategy 必须是 {self.STRATEGIES} 之一")

        os.makedirs(persist_dir, exist_ok=True)
        self.client = chromadb.PersistentClient(
            path=persist_dir,
            settings=Settings(
                anonymized_telemetry=False,
                allow_reset=False,
            ),
        )
        self.persist_dir = persist_dir
        self.distance_function = distance_function
        self.strategy = strategy

    # ==================== 内部辅助方法 ====================

    def _get_single_collection(self):
        """V2: 获取单 collection。"""
        return self.client.get_or_create_collection(
            name=self.SINGLE_COLLECTION_NAME,
            metadata={"hnsw:space": self.distance_function},
        )

    def _get_multi_collection(self, kb_id: int):
        """V1: 获取指定 kb 的 collection。"""
        return self.client.get_or_create_collection(
            name=f"kb_{kb_id}",
            metadata={"hnsw:space": self.distance_function},
        )

    def _get_collection_for_kb(self, kb_id: int):
        """根据 strategy 选择 collection 获取方式。"""
        if self.strategy == "single_collection":
            return self._get_single_collection()
        return self._get_multi_collection(kb_id)

    def _generate_chunk_id(self, chunk: Chunk) -> str:
        """
        生成全局唯一的 chunk ID。

        V2 single_collection: f"kb_{kb_id}_doc_{doc_id}_chunk_{chunk_index}"
        V2 multi_collection: f"{doc_id}_{chunk_index}"（kb_id 已在 collection 名里）
        """
        kb_id = chunk.metadata.get("kb_id")
        doc_id = chunk.metadata.get("doc_id", "unknown")
        chunk_index = chunk.metadata.get("chunk_index", 0)

        if self.strategy == "single_collection":
            return f"kb_{kb_id}_doc_{doc_id}_chunk_{chunk_index}"
        return f"{doc_id}_{chunk_index}"

    def _extract_kb_id(self, chunks: List[Chunk]) -> int:
        """从 chunks 中提取 kb_id（V1 行为：所有 chunks 必须同 kb_id）。"""
        if not chunks:
            raise RetrievalError("chunks 不能为空")
        kb_ids = {c.metadata.get("kb_id") for c in chunks}
        if None in kb_ids:
            raise RetrievalError("每个 chunk 必须包含 metadata['kb_id']")
        if len(kb_ids) > 1:
            raise RetrievalError(
                f"所有 chunks 必须属于同一个 kb_id，当前包含: {kb_ids}"
            )
        return kb_ids.pop()

    # ==================== 核心方法 ====================

    def add(self, chunks: List[Chunk]) -> List[str]:
        """添加 chunks 到向量库。"""
        if not chunks:
            return []

        for i, c in enumerate(chunks):
            if c.embedding is None:
                raise RetrievalError(f"chunk[{i}] 缺少 embedding")

        # 校验单 kb_id（无论 strategy 都要求 chunks 同 kb_id）
        kb_id = self._extract_kb_id(chunks)
        collection = self._get_collection_for_kb(kb_id)

        ids = [c.id or self._generate_chunk_id(c) for c in chunks]
        embeddings = [c.embedding for c in chunks]
        documents = [c.content for c in chunks]
        metadatas = [c.metadata for c in chunks]

        try:
            collection.add(
                ids=ids,
                embeddings=embeddings,
                documents=documents,
                metadatas=metadatas,
            )
        except Exception as e:
            raise RetrievalError(f"Chroma add 失败: {e}") from e

        return ids

    def search(
        self,
        query_embedding: List[float],
        top_k: int = 5,
        filter: Optional[Dict[str, Any]] = None,
    ) -> List[Chunk]:
        """根据查询向量检索最相关的 chunks。"""
        if not filter or "kb_id" not in filter:
            raise RetrievalError("filter 必须包含 kb_id 用于多租户隔离")

        kb_id = filter["kb_id"]
        collection = self._get_collection_for_kb(kb_id)

        # 构造 where 条件
        if self.strategy == "single_collection":
            # 单 collection 必须用 kb_id 过滤
            where = dict(filter)
        else:
            # 多 collection 已经隔离了 kb_id
            where = {k: v for k, v in filter.items() if k != "kb_id"}

        try:
            results = collection.query(
                query_embeddings=[query_embedding],
                n_results=top_k,
                where=where if where else None,
            )
        except Exception as e:
            raise RetrievalError(f"Chroma query 失败: {e}") from e

        ids_list = results["ids"][0]
        docs_list = results["documents"][0]
        metas_list = results["metadatas"][0]
        dists_list = results["distances"][0]

        chunks = []
        for i, chunk_id in enumerate(ids_list):
            score = 1.0 - dists_list[i]
            chunks.append(
                Chunk(
                    id=chunk_id,
                    content=docs_list[i],
                    metadata=metas_list[i],
                    score=score,
                )
            )
        return chunks

    def delete_by_doc_id(self, doc_id: int) -> int:
        """删除指定文档的所有 chunks。"""
        deleted_count = 0

        if self.strategy == "single_collection":
            # V2 优化：一次 where 查询搞定
            collection = self._get_single_collection()
            try:
                result = collection.delete(where={"doc_id": doc_id})
                if isinstance(result, dict):
                    deleted_count = result.get("deleted", 0)
                elif isinstance(result, list):
                    deleted_count = len(result)
            except Exception as e:
                raise RetrievalError(f"Chroma delete 失败: {e}") from e
        else:
            # V1 行为：遍历所有 kb_* collections
            for collection_info in self.client.list_collections():
                if not collection_info.name.startswith("kb_"):
                    continue
                collection = self.client.get_collection(collection_info.name)
                try:
                    result = collection.delete(where={"doc_id": doc_id})
                    if isinstance(result, dict):
                        deleted_count += result.get("deleted", 0)
                    elif isinstance(result, list):
                        deleted_count += len(result)
                except Exception as e:
                    print(f"  ⚠️  collection {collection_info.name} delete 失败: {e}")

        return deleted_count

    # ==================== 扩展方法 ====================

    def delete_all(self) -> int:
        """清空所有数据。"""
        deleted = 0
        if self.strategy == "single_collection":
            try:
                collection = self._get_single_collection()
                count = collection.count()
                collection.delete(where={})
                deleted = count
            except Exception:
                pass
        else:
            for info in self.client.list_collections():
                if info.name.startswith("kb_"):
                    col = self.client.get_collection(info.name)
                    count = col.count()
                    col.delete(where={})
                    deleted += count
        return deleted

    def count(self) -> int:
        """返回所有 chunks 总数。"""
        if self.strategy == "single_collection":
            return self._get_single_collection().count()
        total = 0
        for info in self.client.list_collections():
            if info.name.startswith("kb_"):
                total += self.client.get_collection(info.name).count()
        return total


__all__ = ["ChromaVectorStore"]