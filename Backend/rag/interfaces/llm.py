# rag/interfaces/llm.py
"""
LLM 接口定义。

为什么需要这个接口：
    LLM 提供商有多种实现（mmx / MiniMax、OpenAI、DeepSeek、Anthropic...），
    业务代码不应该知道具体用了哪家。定义接口后，换 LLM 只改 factory.py。

依赖倒置原则（DIP）：
    高层模块依赖本接口，不依赖具体 LLM SDK。

修复历史：
    V0.1 依赖了 langchain_core.messages.BaseMessage，绑死 LangChain。
    V0.2 定义自己的 Message 数据结构，接口层零外部依赖。

设计原则：先小后大
    V0 阶段 LLM 接口只暴露最核心的 chat(messages) → str。
    流式输出、工具调用等高级特性等 V3 用到时再加，避免 V0 阶段过度设计。
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Optional


@dataclass
class Message:
    """
    对话消息。

    为什么不用 LangChain 的 BaseMessage：
        接口层零外部依赖。实现层（mmx、openai）可以内部转成
        LangChain 或各家 SDK 的格式，对外只暴露 Message。

    Attributes:
        role: 角色，"system" / "user" / "assistant"
        content: 消息内容
    """

    role: str  # "system" / "user" / "assistant"
    content: str


class LLMInterface(ABC):
    """
    LLM 模型抽象接口。

    所有 LLM 实现（mmx、OpenAI、DeepSeek 等）都必须继承此类。
    """

    # ==================== 核心方法（必须实现） ====================

    @abstractmethod
    async def chat(
        self,
        messages: List[Message],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ) -> str:
        """
        根据消息列表生成回复。

        Args:
            messages: 对话消息列表（通常 [SystemMessage, UserMessage, ...]）
            temperature: 温度参数（0.0-1.0），控制随机性
            max_tokens: 最大生成 token 数

        Returns:
            LLM 生成的文本回复

        Raises:
            APIError: 当 LLM API 调用失败时
            ValueError: 当 messages 为空时

        Note:
            实现要点：
            - V3 阶段实现 mmx 版本时，直接调 mmx.chat() 即可
            - temperature / max_tokens 可选，实现层有自己的默认值
            - 不在本接口承诺流式输出或工具调用（见扩展方法）
        """
        raise NotImplementedError

    @property
    @abstractmethod
    def model_name(self) -> str:
        """
        返回模型名称。

        用于日志和调试，例如 "MiniMax-Text-01"。
        """
        raise NotImplementedError

    # ==================== 扩展方法（V0 不实现，V3+ 按需加） ====================
    # V0 阶段不写流式/工具调用等抽象方法。
    # 等到 V3 写 mmx 实现时，发现"我需要流式输出"，再回来加 chat_stream 抽象方法。
    # 这就是"先小后大"——避免 V0 阶段堆一堆还没想清楚的方法。