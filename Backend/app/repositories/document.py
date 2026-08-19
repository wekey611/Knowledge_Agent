from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.knowledge import Document


class DocumentRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, document: Document) -> Document:
        self.db.add(document)
        await self.db.commit()
        await self.db.refresh(document)

        return document

    async def get_list(self, kb_id: int):
        stmt = select(Document).where(Document.kb_id == kb_id)
        result = await self.db.execute(stmt)
        documents = result.scalars().all()

        return {
            "total": len(documents),
            "data": documents
        }

    async def get_detail(self, kb_id: int, document_id: int):
        stmt = select(Document).where(Document.kb_id == kb_id, Document.id == document_id)
        result = await self.db.execute(stmt)
        return result.scalars().first()

    async def delete(self, kb_id: int, document_id: int) -> bool:
        stmt = select(Document).where(Document.kb_id == kb_id, Document.id == document_id)
        result = await self.db.execute(stmt)
        document = result.scalars().first()
        if document is None:
            return False

        await self.db.delete(document)
        await self.db.commit()
        return True
