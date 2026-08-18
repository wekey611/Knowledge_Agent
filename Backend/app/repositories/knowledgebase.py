from fastapi import HTTPException
from mako.testing.helpers import result_lines
from sqlalchemy import select, delete, exists, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from starlette import status
from app import models, schemas, settings


class KnowledgeRepository:
    def __init__(self, db=AsyncSession):
        self.db = db

    async def create(self, owner_id, data):
        kb = models.knowledge.KnowledgeBase(
            name=data.name,
            description=data.description,
            owner_id=owner_id,
            scope=data.scope,
            org_id=data.org_id,
            chunk_size=data.chunk_size,
            chunk_overlap=data.chunk_overlap,
        )

        self.db.add(kb)
        await  self.db.commit()
        await self.db.refresh(kb)
        return kb

    # 获取知识库列表
    async def get_bases(self, user_id):
        org_member_exists = exists().where(
            models.auth.OrganizationMember.org_id == models.knowledge.KnowledgeBase.org_id,
            models.auth.OrganizationMember.user_id == user_id
        )
        stmt = (
            select(models.knowledge.KnowledgeBase)
            .where(
                models.knowledge.KnowledgeBase.deleted == False,
                or_(
                    (models.knowledge.KnowledgeBase.scope == "personal")
                    & (models.knowledge.KnowledgeBase.owner_id == user_id),

                    (models.knowledge.KnowledgeBase.scope == "org")
                    & org_member_exists,

                    models.knowledge.KnowledgeBase.scope == "public",
                )
            )
            .order_by(
                models.knowledge.KnowledgeBase.created_at.desc()
            )
        )

        result = await self.db.execute(stmt)
        return result.scalars().all()

    # 获取知识库详情
    async def get_base(self, id):
        stmt = select(models.knowledge.KnowledgeBase).where(
            models.knowledge.KnowledgeBase.id == id,
            models.knowledge.KnowledgeBase.deleted == False,
        )
        result = await self.db.execute(stmt)
        return result.scalars().one_or_none()

    # 获取个人知识库数量
    async def count_personal(self, owner_id):
        stmt = select(models.knowledge.KnowledgeBase).where(
            models.knowledge.KnowledgeBase.scope == models.knowledge.KnowledgeSource.PERSONAL,
            models.knowledge.KnowledgeBase.owner_id == owner_id,
            models.knowledge.KnowledgeBase.deleted == False)
        result = await self.db.execute(stmt)
        count = len(result.scalars().all())
        return count

    # 校验知识库名称是否已存在
    async def exists_by_name(
            self,
            name: str,
            scope: models.knowledge.KnowledgeSource,
            owner_id: int,
            org_id: int | None = None
    ):
        stmt = select(models.knowledge.KnowledgeBase).where(
            models.knowledge.KnowledgeBase.name == name,
            models.knowledge.KnowledgeBase.scope == scope,
            models.knowledge.KnowledgeBase.owner_id == owner_id,
            models.knowledge.KnowledgeBase.org_id == org_id,
            models.knowledge.KnowledgeBase.deleted == False
        )
        result = await self.db.execute(stmt)
        return result.scalars().one_or_none()

    # 更新知识库详情
    # 更新知识库
    async def update(self, id, data):
        stmt = select(models.knowledge.KnowledgeBase).where(models.knowledge.KnowledgeBase.id == id)
        result = await self.db.execute(stmt)
        kb = result.scalars().one_or_none()
        if kb:
            kb.name = data.name
            kb.description = data.description
            if data.chunk_size:
                kb.chunk_size = data.chunk_size
            if data.chunk_overlap:
                kb.chunk_overlap = data.chunk_overlap

        await self.db.commit()
        await self.db.refresh(kb)
        return kb

    # 删除知识库（软删除）
    async def delete(self, id):
        stmt = select(models.knowledge.KnowledgeBase).where(
            models.knowledge.KnowledgeBase.id == id,
            models.knowledge.KnowledgeBase.deleted == False,
        )
        result = await self.db.execute(stmt)
        kb = result.scalars().one_or_none()
        if kb is None:
            return None

        kb.deleted = True
        await self.db.commit()
        await self.db.refresh(kb)
        return kb
