"""
评测集加载。

支持 JSON 格式，每条样本：
    {
        "question": "问题",
        "expected_answer": "期望答案（可选）",
        "relevant_chunk_keywords": ["关键词1", "关键词2"],  # 用于检索评估
        "kb_id": 1
    }
"""
import json
from dataclasses import dataclass
from pathlib import Path
from typing import List


@dataclass
class EvalSample:
    """单条评测样本。"""
    question: str
    kb_id: int
    expected_answer: str = ""
    relevant_chunk_keywords: List[str] = None  # 用于判断检索是否命中

    def __post_init__(self):
        if self.relevant_chunk_keywords is None:
            self.relevant_chunk_keywords = []


def load_eval_dataset(path: str) -> List[EvalSample]:
    """
    从 JSON 文件加载评测集。

    Args:
        path: JSON 文件路径

    Returns:
        List[EvalSample]
    """
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"评测集文件不存在: {path}")

    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    samples = []
    for item in data:
        samples.append(EvalSample(
            question=item["question"],
            kb_id=item.get("kb_id", 1),
            expected_answer=item.get("expected_answer", ""),
            relevant_chunk_keywords=item.get("relevant_chunk_keywords", []),
        ))

    return samples


__all__ = ["EvalSample", "load_eval_dataset"]