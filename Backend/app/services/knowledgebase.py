from app import repositories, schemas, models, core, settings
from app.core.database import get_db, AsyncSession
from fastapi import HTTPException
from starlette import status


class KnowledgeBaseService:

    def __init__(self, db: AsyncSession):
        self.repo = repositories.knowledgebase.KnowledgeRepository(db)

    # 新建
    async def create(self, current_user,
                     data: schemas.knowledgebase.KnowledgeBaseCreate):

        # 检测该用户是否能在该区域创建base
        scope = data.scope
        if scope == models.knowledge.KnowledgeSource.PUBLIC:
            await  core.permissions.require_admin(current_user)

        elif scope == models.knowledge.KnowledgeSource.ORG:
            if data.org_id is None:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="创建组织知识库必须指定组织")
            await core.permissions.check_org_admin(data.org_id, current_user, self.repo.db)

        elif scope == models.knowledge.KnowledgeSource.PERSONAL:
            if data.org_id is not None:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="创建个人知识库不能指定组织")

            count = await self.repo.count_personal(owner_id=current_user.id)

            if count >= settings.PERSONAL_KB_LIMIT:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                    detail=f"个人知识库最多创建{settings.PERSONAL_KB_LIMIT}个")

        # 检测知识库名称是否为空
        if not data.name:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail="知识库名称不能为空")

        # 检测分块大小和重叠
        if data.chunk_size < 100 or data.chunk_overlap < 0:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                                detail="分块大小必须大于100，重叠必须大于0")

        if data.chunk_size < data.chunk_overlap:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="分块大小必须大于重叠")

        # 检测知识库是否重复
        exists = await self.repo.exists_by_name(
            name=data.name,
            scope=data.scope,
            owner_id=current_user.id,
            org_id=data.org_id,
        )
        if exists:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="知识库名称重复")

        # 提交给repo
        kb = await self.repo.create(owner_id=current_user.id, data=data)
        return kb

    # 获取个人知识库列表
    async def get_bases(self, current_user):
        bases = await self.repo.get_bases(
            user_id=current_user.id
        )

        return {
            "total": len(bases),
            "data": bases,
        }
