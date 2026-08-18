import hashlib
from pathlib import Path

from fastapi import UploadFile, HTTPException
from starlette import status

from app import core
from app.models.knowledge import KnowledgeSource, Document
from app.models.user import User
from app.repositories.document import DocumentRepository
from app.services.storage import StorageService
from app.repositories.knowledgebase import KnowledgeRepository


class DocumentService:

    def __init__(self, db):
        self.db = db
        self.repo = DocumentRepository(db)
        self.kb_repo = KnowledgeRepository(db)
        self.storage = StorageService()

    async def upload(
            self,
            kb_id: int,
            user: User,
            file: UploadFile,
    ):

        # 1. 获取知识库
        kb = await self.kb_repo.get_base(kb_id)
        if kb is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="知识库不存在")
        if kb.scope == KnowledgeSource.PUBLIC:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="无权限访问")
        elif kb.scope == KnowledgeSource.ORG:
            await core.permissions.check_org_admin(kb.org_id, user, self.repo.db)
        elif kb.scope == KnowledgeSource.PERSONAL:
            if kb.owner_id != user.id:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="无权限访问")

        # 2.读取文件
        content = await file.read()

        # 3. 保存文件
        storage_path = await self.storage.save(kb_id=kb.id, filename=file.filename, content=content)

        # 4. 创建数据库记录
        document = Document(
            kb_id=kb.id,
            uploader_id=user.id,
            title=file.filename,
            filename=file.filename,
            file_type=Path(file.filename).suffix.lstrip(".").lower(),
            mime_type=file.content_type,
            file_size=len(content),
            file_hash=hashlib.sha256(content).hexdigest(),
            storage_key=storage_path,
        )
        await self.repo.create(document)

        return document
