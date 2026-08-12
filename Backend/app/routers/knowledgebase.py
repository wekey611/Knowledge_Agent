from fastapi import APIRouter, status, Depends, Path
from app import repositories, core, schemas, models, services
from app.core.database import get_db, AsyncSession

router = APIRouter(
    prefix="/knowledge-bases",
    tags=["knowledge"]
)


# 创建知识库
@router.post("", status_code=status.HTTP_201_CREATED, response_model=schemas.knowledgebase.KnowledgeBaseDetail)
async def create_knowledge_base(
        data: schemas.knowledgebase.KnowledgeBaseCreate,
        current_user: models.user.User = Depends(core.oauth2.get_current_user),
        db: AsyncSession = Depends(get_db)
):
    service = services.knowledgebase.KnowledgeBaseService(db)
    return await service.create(current_user=current_user, data=data)


# 查看知识库列表
@router.get("", response_model=schemas.knowledgebase.KnowledgeBaseList)
async def get_knowledge_base(
        current_user: models.user.User = Depends(core.oauth2.get_current_user),
        db: AsyncSession = Depends(get_db)
):
    service=services.knowledgebase.KnowledgeBaseService(db)
    return await service.get_bases(current_user=current_user)