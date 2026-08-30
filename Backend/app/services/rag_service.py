"""
RAG 业务服务：封装权限检查 + Pipeline 调用。
"""
from typing import Optional

from app import core
from rag.config import load_config
from rag.factory import build_pipeline
from rag.pipeline import RAGResponse


class RAGService:
    """
    RAG 业务编排。

    Attributes:
        db: 数据库 session
    """

    def __init__(self, db):
        self.db = db

    async def query(
        self,
        kb_id: int,
        user_query: str,
        current_user,
        top_k: Optional[int] = None,
    ) -> RAGResponse:
        """
        知识库问答。

        Args:
            kb_id: 知识库 ID
            user_query: 用户问题
            current_user: 当前登录用户
            top_k: 检索数量（None 用默认）

        Returns:
            RAGResponse 含答案 + 引用来源
        """
        # 1. 权限检查
        await core.permissions.check_knowledge_base_access(
            kb_id=kb_id, current_user=current_user, db=self.db
        )

        # 2. 构造 Pipeline 并查询
        config = load_config()
        pipeline = build_pipeline(config)

        response = await pipeline.query(
            query=user_query,
            kb_id=kb_id,
            top_k=top_k,
        )

        return response


__all__ = ["RAGService"]