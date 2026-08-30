"""
Fake LLM：测试用，返回固定字符串。

V3: 用于单元测试和开发调试，不需要真实 LLM。
"""
from typing import List, Optional

from rag.interfaces.llm import LLMInterface, Message


class FakeLLM(LLMInterface):
    """
    测试用 LLM。

    Attributes:
        response: 固定的回复内容
        model_name: 报告的模型名
    """

    def __init__(
        self,
        response: str = "这是一个测试回答。",
        model_name: str = "fake-model",
    ):
        self._fixed_response = response
        self._model_name = model_name

    async def chat(
        self,
        messages: List[Message],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ) -> str:
        """直接返回固定响应。"""
        return self._fixed_response

    @property
    def model_name(self) -> str:
        return self._model_name


__all__ = ["FakeLLM"]