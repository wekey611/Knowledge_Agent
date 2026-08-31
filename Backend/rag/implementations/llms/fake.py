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

    # ---- RAGAS 兼容：让 FakeLLM 能当 RAGAS judge 使用 ----
    # RAGAS 0.2 期望 judge LLM 有 set_run_config / get_temperature 等接口。
    # FakeLLM 不调 API，所以这些都是 no-op。
    def set_run_config(self, run_config):
        """RAGAS 兼容：保存运行配置（fake LLM 忽略）。"""
        self._run_config = run_config

    def get_temperature(self, n: int = 1) -> float:
        """RAGAS 兼容：fake LLM 固定 temperature=0。"""
        return 0.0

    async def generate_text(self, *args, **kwargs):
        """RAGAS 兼容：直接返回固定响应（同步版）。"""
        return self._fixed_response

    async def agenerate_text(self, prompt=None, n: int = 1, temperature=None, stop=None, callbacks=None):
        """RAGAS 兼容：异步生成（fake 直接返回）。"""
        from langchain_core.outputs import LLMResult, Generation
        # 构造 RAGAS 期望的 LLMResult 格式
        return LLMResult(generations=[[Generation(text=self._fixed_response)]])

    # ---- 兼容 RAGAS 不同代码路径的别名 ----
    # RAGAS 0.2 在 pydantic_prompt.py:187 写：
    #   resp = await llm.generate(prompt_value, n, temperature, stop, callbacks)
    # 所以 generate 必须是 async 函数（awaitable）。
    # LangchainLLMWrapper 内部还有 generate_text/agenerate_text（同步版），
    # 我们之前都覆盖了，这里再补 async generate。
    async def generate(self, *args, **kwargs):
        """RAGAS 兼容：异步版，prompt.generate() 会 await 这个。"""
        from langchain_core.outputs import LLMResult, Generation
        return LLMResult(generations=[[Generation(text=self._fixed_response)]])

    async def agenerate(self, *args, **kwargs):
        """RAGAS 兼容异步别名（部分代码路径用这个）。"""
        from langchain_core.outputs import LLMResult, Generation
        return LLMResult(generations=[[Generation(text=self._fixed_response)]])

    def is_finished(self, response) -> bool:
        """RAGAS 兼容：fake LLM 总是 finished。"""
        return True

    def __getattr__(self, name):
        # 关键：raise AttributeError（不是返回 lambda）。
        # RAGAS 内部用 hasattr() 检查方法是否存在，
        # 返回 lambda 会让 hasattr() = True，但调用时返回 None，await None 报错。
        # raise AttributeError 让 hasattr() = False，RAGAS 会走 fallback 路径。
        raise AttributeError(f"FakeLLM has no attribute {name!r}")


__all__ = ["FakeLLM"]