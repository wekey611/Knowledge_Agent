"""
RAGAS 兼容的评测集加载（V2 版）。

与 V4 dataset.py 的区别：
    V4 (EvalSample)：只支持关键词匹配，字段对不上 RAGAS
    V2 (EvalSampleV2)：原生支持 RAGAS 的 reference_contexts 字段

向后兼容：
    如果 JSON 里没 reference_contexts 字段，自动用 reference 作兜底。
    这能让老 sample_qa.json（只有 expected_answer）也能跑，但 Context Recall
    指标会偏低（只比对答案字符串相似度，不是真正的 chunk 相似度）。

JSON 格式：
    [
      {
        "question": "年假怎么申请？",
        "kb_id": 1,
        "expected_answer": "提前 3 天提交",
        "reference_contexts": [
          "员工申请年假须提前 3 天提交申请单，经主管审批后生效。"
        ],
        "relevant_chunk_keywords": ["提前 3 天", "年假申请"]  # 可选，V4 兼容
      }
    ]
"""
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional

from rag.evaluation.dataset import EvalSample  # 复用 V4 的 EvalSample


@dataclass
class EvalSampleV2:
    """
    RAGAS 兼容的评测样本。

    Attributes:
        question: 用户问题（RAGAS: user_input）
        kb_id: 知识库 ID
        expected_answer: 标准答案文本（RAGAS: reference）
        reference_contexts: 标准答案所在的原文段落列表（RAGAS: reference_contexts）
            这是 RAGAS Context Recall 的 ground truth。
            推荐从文档里直接摘录完整段落，不要自己改写。
        relevant_chunk_keywords: 兼容 V4 的关键词（可选，新代码建议忽略）
    """

    question: str
    kb_id: int
    expected_answer: str = ""
    reference_contexts: List[str] = field(default_factory=list)
    relevant_chunk_keywords: List[str] = field(default_factory=list)

    @classmethod
    def from_v4(cls, v4: EvalSample) -> "EvalSampleV2":
        """
        从 V4 EvalSample 转换（兜底：用 expected_answer 作 reference_contexts）。
        用于让老样本也能跑 RAGAS（Context Recall 会偏低）。
        """
        return cls(
            question=v4.question,
            kb_id=v4.kb_id,
            expected_answer=v4.expected_answer,
            reference_contexts=[v4.expected_answer] if v4.expected_answer else [],
            relevant_chunk_keywords=v4.relevant_chunk_keywords,
        )


def load_eval_dataset_v2(path: str) -> List[EvalSampleV2]:
    """
    从 JSON 文件加载 V2 评测集。

    Args:
        path: JSON 路径

    Returns:
        List[EvalSampleV2]

    Raises:
        FileNotFoundError: 文件不存在
        ValueError: JSON 缺少必需字段
    """
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"评测集文件不存在: {path}")

    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    samples = []
    for i, item in enumerate(data):
        if "question" not in item:
            raise ValueError(f"第 {i+1} 条样本缺少 question 字段")

        samples.append(
            EvalSampleV2(
                question=item["question"],
                kb_id=item.get("kb_id", 1),
                expected_answer=item.get("expected_answer", ""),
                reference_contexts=item.get("reference_contexts", []),
                relevant_chunk_keywords=item.get("relevant_chunk_keywords", []),
            )
        )

    return samples


def to_ragas_samples(
    samples: List[EvalSampleV2],
    retrieved_chunks_by_question: Optional[dict] = None,
    answers_by_question: Optional[dict] = None,
) -> list:
    """
    把 EvalSampleV2 转成 RAGAS 的 SingleTurnSample 列表。

    Args:
        samples: V2 样本列表
        retrieved_chunks_by_question: {question: List[str]} 检索结果（运行时填）
        answers_by_question: {question: str} LLM 答案（运行时填）

    Returns:
        List[SingleTurnSample]（RAGAS 0.2 期望的格式）
    """
    # 必须先 apply_compat_patches() 才能 import ragas
    from rag.evaluation.ragas_compat import apply_compat_patches
    apply_compat_patches()

    from ragas.dataset_schema import SingleTurnSample

    ragas_samples = []
    for s in samples:
        retrieved = (retrieved_chunks_by_question or {}).get(s.question, [])
        answer = (answers_by_question or {}).get(s.question, "")

        ragas_samples.append(
            SingleTurnSample(
                user_input=s.question,
                retrieved_contexts=retrieved,
                reference_contexts=s.reference_contexts or None,
                response=answer or None,
                reference=s.expected_answer or None,
            )
        )

    return ragas_samples


__all__ = ["EvalSampleV2", "load_eval_dataset_v2", "to_ragas_samples"]