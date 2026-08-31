"""
RAG HTTP 路由：知识库问答。

V3 接口：
    POST /knowledge-bases/{kb_id}/query
        body: {"query": "...", "top_k": 5}
        response: {"answer": "...", "sources": [...], "query": "..."}
"""
from typing import Optional

from fastapi import APIRouter, Depends, Path
from pydantic import BaseModel, Field

from app import core, models, services
from app.core.database import get_db, AsyncSession
from app.services.rag_service import RAGService
from rag.pipeline import RAGResponse

router = APIRouter(
    prefix="/knowledge-bases",
    tags=["rag"]
)


class QueryRequest(BaseModel):
    """查询请求体。"""
    query: str = Field(..., min_length=1, max_length=2000, description="用户问题")
    top_k: Optional[int] = Field(default=None, ge=1, le=20, description="检索数量（默认 5）")


class SourceItem(BaseModel):
    """引用来源项。"""
    chunk_id: str
    score: float | None = None
    source_file: str
    preview: str


class QueryResponse(BaseModel):
    """查询响应。"""
    query: str
    answer: str
    sources: list[SourceItem]


@router.post(
    "/{kb_id}/query",
    response_model=QueryResponse,
    status_code=200,
)
async def query_knowledge_base(
        kb_id: int = Path(..., description="Knowledge Base ID"),
        body: QueryRequest = ...,
        current_user: models.user.User = Depends(core.oauth2.get_current_user),
        db: AsyncSession = Depends(get_db),
):
    """
    知识库问答接口。

    权限：需要知识库读权限。
    """
    service = RAGService(db)
    response = await service.query(
        kb_id=kb_id,
        user_query=body.query,
        current_user=current_user,
        top_k=body.top_k,
    )
    return response