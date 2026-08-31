"""
简化版评估指标（V4，LEGACY）。

⚠️ V5 RAGAS 接入后，此模块保留作为 keyword 匹配的简易 fallback。
新代码请用：rag/evaluation/ragas_judge.py + ragas 库。

V4 自建指标（不需要 LLM-as-judge）：
    - Context Recall@K：检索结果中是否包含相关 chunk
    - Context Precision@K：检索结果中相关 chunk 的占比
    - Answer Match（简单字符串包含）：答案是否包含期望关键词

V5 RAGAS 指标：
    - Faithfulness：答案是否基于 context（LLM 评）
    - Answer Relevancy：答案是否答了问题（LLM 评）
    - Context Precision：检索结果中相关 chunk 的占比（LLM + Embedding）
    - Context Recall：是否召回了所有相关 chunk（LLM 评）
"""
from typing import List

from rag.evaluation.dataset import EvalSample
from rag.interfaces.vector_store import Chunk


def context_recall_at_k(
    retrieved_chunks: List[Chunk],
    keywords: List[str],
) -> float:
    """
    Context Recall@K：检索结果中**至少包含一个相关 chunk** = 1，否则 0。

    简化版：用关键词匹配判断相关性（不调用 LLM）。
    真正的 Recall 需要标注"哪些 chunk_id 是相关的"，V4 简化处理。
    """
    if not keywords:
        return 1.0  # 无标注时给满分（保守处理）

    for chunk in retrieved_chunks:
        # 如果 chunk 内容包含任一关键词，算命中
        if any(kw in chunk.content for kw in keywords):
            return 1.0
    return 0.0


def context_precision_at_k(
    retrieved_chunks: List[Chunk],
    keywords: List[str],
) -> float:
    """
    Context Precision@K：检索结果中相关 chunk 的占比。
    """
    if not keywords or not retrieved_chunks:
        return 0.0

    relevant = sum(
        1 for c in retrieved_chunks
        if any(kw in c.content for kw in keywords)
    )
    return relevant / len(retrieved_chunks)


def answer_match(answer: str, expected: str) -> float:
    """
    Answer Match：答案是否包含期望答案（简化版字符串匹配）。

    1.0 = 完全包含期望答案
    0.0 = 不包含
    0.5 = 部分包含
    """
    if not expected:
        return 1.0

    if expected in answer:
        return 1.0

    # 部分匹配：期望答案 50% 以上出现在 answer 里
    match_count = sum(1 for c in expected if c in answer)
    return min(1.0, match_count / len(expected)) if expected else 0.0


def evaluate_sample(
    sample: EvalSample,
    retrieved_chunks: List[Chunk],
    answer: str,
) -> dict:
    """对单条样本算所有指标。返回字典里包含 question/answer/expected_answer，
    这样调用方可以打印『期望 vs 实际』对比而不只是指标。
    """
    return {
        "question": sample.question,
        "expected_answer": sample.expected_answer,
        "answer": answer,
        "context_recall@k": context_recall_at_k(retrieved_chunks, sample.relevant_chunk_keywords),
        "context_precision@k": context_precision_at_k(retrieved_chunks, sample.relevant_chunk_keywords),
        "answer_match": answer_match(answer, sample.expected_answer),
        "retrieved_count": len(retrieved_chunks),
    }


def aggregate_metrics(results: List[dict]) -> dict:
    """聚合所有样本的指标，算平均值。"""
    if not results:
        return {}

    keys = ["context_recall@k", "context_precision@k", "answer_match"]
    aggregated = {}
    for k in keys:
        values = [r[k] for r in results]
        aggregated[k] = round(sum(values) / len(values), 4)

    aggregated["sample_count"] = len(results)
    return aggregated


__all__ = [
    "context_recall_at_k",
    "context_precision_at_k",
    "answer_match",
    "evaluate_sample",
    "aggregate_metrics",
]