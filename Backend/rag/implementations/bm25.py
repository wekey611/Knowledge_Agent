"""
BM25 关键词检索器（补充向量检索）。

为什么需要 BM25：
    - 向量检索擅长"语义相似"，但对"精确关键词"不敏感
    - BM25 是经典关键词检索（Lucene/Elasticsearch 用的）
    - 混合检索（向量 + BM25）能提升召回率

依赖：
    pip install rank_bm25
"""
from typing import List, Tuple

from rank_bm25 import BM25Okapi


class BM25Retriever:
    """
    BM25 关键词检索器（内存版）。

    Attributes:
        documents: 文档列表（已分词）
        bm25: BM25Okapi 实例
    """

    def __init__(self, documents: List[str]):
        """
        Args:
            documents: 文档原文列表（内部会自动分词）
        """
        # 中文简单分词：每个字符当一个 token（V5 简化）
        # V5 优化：可换 jieba 分词
        self.tokenized_docs = [self._tokenize(doc) for doc in documents]
        self.bm25 = BM25Okapi(self.tokenized_docs)

    @staticmethod
    def _tokenize(text: str) -> List[str]:
        """简单分词（按字切分）。"""
        # 去掉空格，按字符切
        return list(text.replace(" ", "").replace("\n", ""))

    def search(self, query: str, top_k: int = 5) -> List[Tuple[int, float]]:
        """
        检索 query 相关的文档。

        Returns:
            [(doc_index, score), ...] 按 score 降序
        """
        tokenized_query = self._tokenize(query)
        scores = self.bm25.get_scores(tokenized_query)

        # 排序取 top_k
        indexed_scores = list(enumerate(scores))
        indexed_scores.sort(key=lambda x: x[1], reverse=True)
        return indexed_scores[:top_k]


__all__ = ["BM25Retriever"]