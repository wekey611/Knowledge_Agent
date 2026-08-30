# rag/implementations/llms/mmx.py
"""
minimax LLM 实现。

依赖：
    pip install openai

环境变量：
    MINIMAX_API_KEY: minimax API 密钥
"""
import os
from typing import List, Optional
from openai import AsyncOpenAI

from rag.interfaces.llm import LLMInterface, Message


class MiniMaxLLM(LLMInterface):
    """
    MiniMax LLM 实现（纯异步）。

    使用 OpenAI SDK 调用 MiniMax API，因为 MiniMax 兼容 OpenAI 接口。

    Attributes:
        model: 模型名称，如 "mmx-v4-flash" 或 "mmx-v4-pro"
        temperature: 默认温度
        max_tokens: 默认最大 token 数
    """

    def __init__(
            self,
            api_key: Optional[str] = None,
            model: str = "MiniMax-M2.7-highspeed",
            base_url: str = "https://api.minimaxi.com/v1",
            temperature: float = 0.0,
            max_tokens: int = 4096
    ):
        """
        Args:
            api_key: MiniMax API 密钥，不传则从环境变量 MINIMAX_API_KEY 读取
            model: 模型名称
            base_url: API 地址
            temperature: 默认温度
            max_tokens: 默认最大 token 数
        """
        self.api_key = api_key or os.environ.get("MINIMAX_API_KEY")
        self.model = model
        self.base_url = base_url
        self.temperature = temperature
        self.max_tokens = max_tokens
        self._model_name = model

        if not self.api_key:
            raise ValueError(
                "MINIMAX_API_KEY is not set. "
                "Please set it in environment variables or pass api_key parameter."
            )

        # 异步客户端
        self.client = AsyncOpenAI(
            api_key=self.api_key,
            base_url=self.base_url
        )

    async def chat(
            self,
            messages: List[Message],
            temperature: Optional[float] = None,
            max_tokens: Optional[int] = None,
    ) -> str:
        """
        异步生成回复。

        Args:
            messages: Message 列表（role: system/user/assistant）
            temperature: 温度参数，不传则使用默认值
            max_tokens: 最大 token 数，不传则使用默认值

        Returns:
            LLM 生成的文本

        Raises:
            RuntimeError: API 调用失败
            ValueError: messages 为空
        """
        if not messages:
            raise ValueError("messages 不能为空")

        # 将自定义 Message 转换为 OpenAI 格式
        openai_messages = [
            {"role": msg.role, "content": msg.content}
            for msg in messages
        ]

        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=openai_messages,
                temperature=temperature or self.temperature,
                max_tokens=max_tokens or self.max_tokens,
            )
            return response.choices[0].message.content or ""
        except Exception as e:
            raise RuntimeError(f"MiniMax API 调用失败: {e}")

    @property
    def model_name(self) -> str:
        """返回模型名称"""
        return self._model_name