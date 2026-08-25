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

    # 按内容哈希查重（同一知识库内）
    async def get_by_hash(self, kb_id: int, file_hash: str):
        stmt = select(Document).where(
            Document.kb_id == kb_id,
            Document.file_hash == file_hash,
        )
        result = await self.db.execute(stmt)
        return result.scalars().first()

    async def delete(self, kb_id: int, document_id: int) -> str | None:
        stmt = select(Document).where(Document.kb_id == kb_id, Document.id == document_id)
        result = await self.db.execute(stmt)
        document = result.scalars().first()
        if document is None:
            return None

        # 返回 storage_key，供 service 层清理物理文件
        storage_key = document.storage_key
        await self.db.delete(document)
        await self.db.commit()
        return storage_key
