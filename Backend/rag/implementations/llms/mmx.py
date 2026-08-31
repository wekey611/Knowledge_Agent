# rag/implementations/llms/mmx.py
"""
minimax LLM 实现。

依赖：
    pip install openai

环境变量：
    MINIMAX_API_KEY: minimax API 密钥
"""
import asyncio
import os
import random
from typing import List, Optional
from openai import AsyncOpenAI
from openai import (
    APIConnectionError,
    APITimeoutError,
    AuthenticationError,
    PermissionDeniedError,
    RateLimitError,
)

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
            max_tokens: int = 4096,
            max_retries: int = 5,
            retry_base_delay: float = 1.5,
    ):
        """
        Args:
            api_key: MiniMax API 密钥，不传则从环境变量 MINIMAX_API_KEY 读取
            model: 模型名称
            base_url: API 地址
            temperature: 默认温度
            max_tokens: 默认最大 token 数
            max_retries: API 调用失败时的最大重试次数（针对 429/5xx/超时/网络错误）
            retry_base_delay: 指数退避的基准秒数（实际等待 = base * 2^attempt ± 抖动）
        """
        self.api_key = api_key or os.environ.get("MINIMAX_API_KEY")
        self.model = model
        self.base_url = base_url
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.max_retries = max_retries
        self.retry_base_delay = retry_base_delay
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

        # 这些异常立即抛（不重试）：
        #   - AuthenticationError / PermissionDeniedError：API key 无效或无权限
        #   - 其他非限流/网络类的异常（让它自然上浮）
        # 可重试：429 RateLimitError、5xx、连接错误、超时
        retryable = (RateLimitError, APIConnectionError, APITimeoutError)

        last_error: Optional[Exception] = None
        for attempt in range(1, self.max_retries + 1):
            try:
                response = await self.client.chat.completions.create(
                    model=self.model,
                    messages=openai_messages,
                    temperature=temperature or self.temperature,
                    max_tokens=max_tokens or self.max_tokens,
                )
                return response.choices[0].message.content or ""
            except (AuthenticationError, PermissionDeniedError):
                # 认证/权限类错误重试也没用，立即抛出
                raise
            except retryable as e:
                last_error = e
                if attempt >= self.max_retries:
                    break
                # 指数退避 + 抖动，避免雷暴群体重试
                # 序列: 1.5s, 3s, 6s, 12s, ...（base=1.5）
                wait = self.retry_base_delay * (2 ** (attempt - 1))
                wait = wait * (0.8 + 0.4 * random.random())  # ±20% 抖动
                print(
                    f"  ⚠️ mmx API 调用失败 (尝试 {attempt}/{self.max_retries})，"
                    f"{wait:.1f}s 后重试: {type(e).__name__}: {str(e)[:120]}"
                )
                await asyncio.sleep(wait)
            except Exception as e:
                # 未知异常：不重试，立即抛
                raise RuntimeError(f"MiniMax API 调用失败（非重试异常）: {e}") from e

        # 所有重试都耗尽
        raise RuntimeError(
            f"MiniMax API 调用失败（已重试 {self.max_retries} 次）: {last_error}"
        )

    @property
    def model_name(self) -> str:
        """返回模型名称"""
        return self._model_name