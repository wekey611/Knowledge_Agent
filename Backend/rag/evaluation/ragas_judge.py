"""
RAGAS judge / embedding wrapper：把项目已有 LLM/Embedding 接入 RAGAS。

设计原则：
    - Judge LLM（mmx）：通过 langchain ChatOpenAI 包装（mmx 兼容 OpenAI 接口）
    - Embedding（硅基流动 BGE-M3）：直接调 HTTP API，绕过 langchain（保持轻依赖）

关键依赖：
    - langchain_openai：ChatOpenAI 类（base_url 指向 minimax）
    - ragas.llms.base.LangchainLLMWrapper：包装任何 langchain LLM
    - ragas.embeddings.base.BaseRagasEmbeddings：embeddings 抽象基类
"""
from __future__ import annotations

import os
from typing import List, Optional

import requests
from langchain_openai import ChatOpenAI
from ragas.embeddings.base import BaseRagasEmbeddings
from ragas.llms.base import LangchainLLMWrapper

from rag.implementations.embeddings.siliconflow import SiliconFlowEmbedding


# ============================================================
# Judge LLM：mmx → ChatOpenAI → LangchainLLMWrapper
# ============================================================

class MMXRagasLLM:
    """
    把项目里的 MiniMax LLM（mmx）包装成 RAGAS 可用的 LLM judge。

    用法：
        llm = MMXRagasLLM(model="MiniMax-M2.7-highspeed")
        metric.llm = llm   # 指标需要 .llm 属性

    实现路径：
        MiniMax OpenAI-compatible API
            → langchain ChatOpenAI(base_url=minimax)
                → LangchainLLMWrapper（包成 RAGAS BaseRagasLLM）
    """

    def __init__(
        self,
        model: str = "MiniMax-M2.7-highspeed",
        base_url: str = "https://api.minimaxi.com/v1",
        api_key: Optional[str] = None,
        temperature: float = 0.0,
        max_tokens: int = 2048,
        timeout: int = 60,
    ):
        api_key = api_key or os.environ.get("MINIMAX_API_KEY")
        if not api_key:
            raise ValueError(
                "MINIMAX_API_KEY 未设置。请在 .env 里配置或传 api_key 参数。"
            )

        # 构造 langchain 的 ChatOpenAI，base_url 指到 minimax
        # 关键：model 参数会被原样转发到 minimax API
        chat_model = ChatOpenAI(
            model=model,
            openai_api_key=api_key,
            openai_api_base=base_url,
            temperature=temperature,
            max_tokens=max_tokens,
            request_timeout=timeout,
        )

        # 包成 RAGAS 的 LLM
        self._wrapped = LangchainLLMWrapper(langchain_llm=chat_model)

    @property
    def wrapped(self) -> LangchainLLMWrapper:
        """返回 LangchainLLMWrapper 实例（RAGAS 内部用）。"""
        return self._wrapped

    # RAGAS 0.2 指标期望 judge 对象有以下属性/方法
    # 通过委托给 _wrapped 实现
    def __getattr__(self, name):
        # RAGAS 指标通常会访问 self.llm.agenerate_text / .generate_text
        # LangchainLLMWrapper 已经有这些方法
        return getattr(self._wrapped, name)


# ============================================================
# Embedding：硅基流动 BGE-M3 → BaseRagasEmbeddings
# ============================================================

class SiliconFlowRagasEmbeddings(BaseRagasEmbeddings):
    """
    把项目里的 SiliconFlowEmbedding 包装成 RAGAS 用的 embeddings。

    RAGAS 的 Context Precision / Context Recall 需要 embedding 算相似度。
    用和索引时**同一个 embedding 模型**保证评估一致性。

    实现：
        BaseRagasEmbeddings 是抽象类，要实现 4 个方法：
            - embed_query
            - aembed_query
            - embed_documents
            - aembed_documents

        我们委托给 SiliconFlowEmbedding（已经实现了 embed_query/embed_documents），
        async 版本用 asyncio.to_thread 包装（硅基流动 SDK 是同步的）。
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "BAAI/bge-m3",
        timeout: int = 30,
        # 注：SiliconFlowEmbedding 没有 base_url 参数（写死在 BASE_URL 类属性）
    ):
        super().__init__()
        self._impl = SiliconFlowEmbedding(
            api_key=api_key,
            model=model,
            timeout=timeout,
        )

    # ---- 同步版本：直接调底层同步方法，绕过 async/sync loop 切换 ----
    # 为什么不用 asyncio.run/run_until_complete：
    #   RAGAS 0.2 AnswerRelevancy 在 async 评估时，会从 async 上下文调用同步 embed_documents。
    #   asyncio.run / loop.run_until_complete 都会因为"已有 running loop"而报错。
    #   SiliconFlowEmbedding 内部有 _embed_documents_sync（线程池跑 requests），
    #   直接调它，绕开 async 上下文问题。
    def embed_query(self, text: str) -> List[float]:
        return self._impl._embed_documents_sync([text])[0]

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        return self._impl._embed_documents_sync(texts)

    # ---- 异步版本：RAGAS 0.2 异步评估走这里 ----
    async def aembed_query(self, text: str) -> List[float]:
        return self.embed_query(text)  # 底层已经是线程池，同步调即可

    async def aembed_documents(self, texts: List[str]) -> List[List[float]]:
        return self.embed_documents(texts)


__all__ = ["MMXRagasLLM", "SiliconFlowRagasEmbeddings"]