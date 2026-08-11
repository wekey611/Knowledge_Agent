from fastapi import HTTPException
from sqlalchemy import select, delete
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

    async def count_personal(self, owner_id):
        stmt = select(models.knowledge.KnowledgeBase).where(
            models.knowledge.KnowledgeBase.scope == models.knowledge.KnowledgeSource.PERSONAL,
            models.knowledge.KnowledgeBase.owner_id == owner_id)
        result = await self.db.execute(stmt)
        count = len(result.scalars().all())
        return count

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
            models.knowledge.KnowledgeBase.org_id == org_id
        )
        result = await self.db.execute(stmt)
        return result.scalars().one_or_none()

