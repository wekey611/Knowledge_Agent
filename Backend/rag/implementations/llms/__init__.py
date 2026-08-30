"""
LLM 实现。

V3: 包含 FakeLLM（测试）和 MMXChat（MiniMax）。
"""
from rag.implementations.llms.fake import FakeLLM
from rag.implementations.llms.mmx import MiniMaxLLM

__all__ = ["FakeLLM", "MiniMaxLLM"]