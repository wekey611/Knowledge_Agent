"""
硅基流动 Embedding 实现（BAAI/bge-m3）。

为什么选硅基流动：
    - 国内直连，稳定（本地 sentence-transformers 要下载 2GB 模型，CPU 推理慢）
    - 支持 BGE-M3（中文效果极好）
    - OpenAI 兼容 API，未来想换 OpenAI 改 base_url 即可

依赖：
    pip install requests
"""
import asyncio
import os
import time
from typing import List, Optional

import requests

from rag.interfaces.embedding import EmbeddingInterface
from rag.exceptions import EmbeddingError


class SiliconFlowEmbedding(EmbeddingInterface):
    """
    硅基流动 Embedding 实现。

    Attributes:
        api_key: 硅基流动 API key（从环境变量 SILICONFLOW_API_KEY 读取）
        model: 模型名称，默认 BAAI/bge-m3
        batch_size: 每批处理文本数（BGE-M3 推荐 ≤32）
        timeout: 单次请求超时时间（秒）
        max_retries: 失败重试次数
    """

    BASE_URL = "https://api.siliconflow.cn/v1/embeddings"
    BGE_M3_DIM = 1024  # BGE-M3 固定维度

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "BAAI/bge-m3",
        batch_size: int = 32,
        timeout: int = 60,
        max_retries: int = 3,
    ):
        self.api_key = api_key or os.environ.get("SILICONFLOW_API_KEY")
        if not self.api_key:
            raise ValueError(
                "未设置 SILICONFLOW_API_KEY 环境变量，也无法从参数传入"
            )
        self.model = model
        self.batch_size = batch_size
        self.timeout = timeout
        self.max_retries = max_retries

    # ==================== 核心方法（实现 EmbeddingInterface） ====================

    async def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """
        批量向量化文档。

        实现细节：
            - 空列表直接返回（避免无效 API 调用）
            - 分批调用（避免单次请求过大）
            - 同步 requests 放到线程池执行（不阻塞 asyncio 事件循环）
            - 失败时自动重试（指数退避）
        """
        if not texts:
            return []

        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None,
            self._embed_documents_sync,
            texts,
        )

    async def embed_query(self, text: str) -> List[float]:
        """
        向量化单个查询。

        BGE 系列对"文档"和"查询"使用相同的 embedding 接口（不像
        Instructor 那样需要不同前缀），所以这里直接调 _embed_documents_sync。
        """
        loop = asyncio.get_event_loop()
        results = await loop.run_in_executor(
            None,
            self._embed_documents_sync,
            [text],
        )
        return results[0]

    @property
    def dim(self) -> int:
        """向量维度。BGE-M3 = 1024。"""
        return self.BGE_M3_DIM

    # ==================== 内部同步方法（在线程池跑） ====================

    def _embed_documents_sync(self, texts: List[str]) -> List[List[float]]:
        """同步批量向量化（在线程池中调用）。"""
        all_embeddings = []
        for i in range(0, len(texts), self.batch_size):
            batch = texts[i:i + self.batch_size]
            batch_embeddings = self._embed_batch_with_retry(batch)
            all_embeddings.extend(batch_embeddings)
        return all_embeddings

    def _embed_batch_with_retry(self, batch: List[str]) -> List[List[float]]:
        """单批次嵌入，带重试。指数退避：1s, 2s, 4s。"""
        last_error = None
        for attempt in range(1, self.max_retries + 1):
            try:
                return self._embed_batch(batch)
            except requests.exceptions.RequestException as e:
                last_error = e
                if attempt < self.max_retries:
                    wait_seconds = 2 ** (attempt - 1)
                    print(
                        f"  ⚠️调用失败 "
                        f"(尝试 {attempt}/{self.max_retries})，"
                        f"{wait_seconds}s 后重试: {e}"
                    )
                    time.sleep(wait_seconds)
        raise EmbeddingError(
            f" Embedding 调用失败（已重试 {self.max_retries} 次）: {last_error}"
        )

    def _embed_batch(self, texts: List[str]) -> List[List[float]]:
        """单次 API 调用嵌入一批文本。"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        data = {
            "model": self.model,
            "input": texts,
            "encoding_format": "float",
        }
        response = requests.post(
            self.BASE_URL,
            headers=headers,
            json=data,
            timeout=self.timeout,
        )
        response.raise_for_status()
        result = response.json()
        return [item["embedding"] for item in result["data"]]


__all__ = ["SiliconFlowEmbedding"]