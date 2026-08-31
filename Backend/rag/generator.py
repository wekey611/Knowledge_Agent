"""
Generator：根据检索到的 chunks 生成答案。

职责：
    1. 构造 Prompt（system + user + 检索到的 context）
    2. 调用 LLM 生成答案
    3. 强制"只基于资料回答"，减少幻觉
"""
from typing import List, Optional

from rag.interfaces.llm import LLMInterface, Message
from rag.interfaces.vector_store import Chunk


# 默认 Prompt 模板（中文场景）
DEFAULT_SYSTEM_PROMPT = """你是一个严谨的知识库问答助手。请严格遵循以下规则：

1. **唯一依据**：回答必须且仅基于下方【参考资料】中的内容。严禁使用参考资料之外的任何个人知识、常识或推测。
2. **无法回答时**：若【参考资料】中没有足够信息回答用户问题，请直接回复“未找到相关信息”，不得补充、推断或展开说明。
3. **格式要求**：回答应简洁、直接，仅输出答案本身，不重复用户问题，不加额外解释或前缀。


【参考资料】
{context}
"""

DEFAULT_USER_TEMPLATE = """{query}"""


class Generator:
    """
    答案生成器。

    Attributes:
        llm: LLM 实例
        system_prompt: 系统提示词模板（{context} 占位）
        user_template: 用户消息模板（{query} 占位）
    """

    def __init__(
        self,
        llm: LLMInterface,
        system_prompt: Optional[str] = None,
        user_template: Optional[str] = None,
    ):
        self.llm = llm
        self.system_prompt = system_prompt or DEFAULT_SYSTEM_PROMPT
        self.user_template = user_template or DEFAULT_USER_TEMPLATE

    def _format_context(self, chunks: List[Chunk]) -> str:
        """把 chunks 拼成 context 字符串。"""
        if not chunks:
            return "（无参考资料）"

        parts = []
        for i, chunk in enumerate(chunks, 1):
            source = chunk.metadata.get("source_file", "未知来源")
            parts.append(f"[{i}] 来源：{source}\n{chunk.content}")

        return "\n\n---\n\n".join(parts)

    async def generate(
        self,
        query: str,
        chunks: List[Chunk],
    ) -> str:
        """
        生成答案。

        Args:
            query: 用户问题
            chunks: 检索到的相关 chunks

        Returns:
            LLM 生成的答案
        """
        context = self._format_context(chunks)
        system_content = self.system_prompt.format(context=context)
        user_content = self.user_template.format(query=query)

        messages = [
            Message(role="system", content=system_content),
            Message(role="user", content=user_content),
        ]

        return await self.llm.chat(messages)


__all__ = ["Generator"]