import hashlib
from pathlib import Path

from fastapi import UploadFile, HTTPException
from fastapi.responses import FileResponse
from starlette import status

from app import core
from app.models.knowledge import Document
from app.models.user import User
from app.repositories.document import DocumentRepository
from app.services.storage import StorageService
from app.repositories.knowledgebase import KnowledgeRepository

PREVIEW_TYPES = {"pdf", "txt", "md"}


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

        # 方案A：仅知识库创建者可上传（全 scope 统一）
        if kb.owner_id != user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="无权限访问")

        # 2.读取文件
        content = await file.read()

        # 3. 查重：同一知识库内相同内容拒绝（策略A）
        file_hash = hashlib.sha256(content).hexdigest()
        exists = await self.repo.get_by_hash(kb_id=kb.id, file_hash=file_hash)
        if exists:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="该文件已存在于知识库中",
            )

        # 4. 保存文件
        storage_path = await self.storage.save(kb_id=kb.id, filename=file.filename, content=content)

        # 5. 创建数据库记录
        document = Document(
            kb_id=kb.id,
            uploader_id=user.id,
            title=file.filename,
            filename=file.filename,
            file_type=Path(file.filename).suffix.lstrip(".").lower(),
            mime_type=file.content_type,
            file_size=len(content),
            file_hash=file_hash,
            storage_key=storage_path,
        )
        await self.repo.create(document)

        # 6. 更新知识库统计（文档数 +1，chunk 数先按 +0，等解析完成后回填）
        await self.kb_repo.increment_counts(kb_id=kb.id, doc_delta=1, chunk_delta=0)

        # increment_counts 内部 commit 会使 document 对象过期（expire_on_commit），
        # 重新 refresh 避免 Pydantic 序列化时触发懒加载 → MissingGreenlet
        await self.db.refresh(document)

        return document

    async def get_list(self, kb_id: int, current_user):
        await core.permissions.check_knowledge_base_access(
            kb_id=kb_id, current_user=current_user, db=self.repo.db)
        return await self.repo.get_list(kb_id)

    async def get_detail(self, kb_id: int, document_id: int, current_user):
        await core.permissions.check_knowledge_base_access(
            kb_id=kb_id, current_user=current_user, db=self.repo.db)
        document = await self.repo.get_detail(kb_id, document_id)
        if document is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="文件不存在")
        return document

    async def delete(self, kb_id: int, document_id: int, current_user):
        await core.permissions.check_knowledge_base_owner(
            kb_id=kb_id, current_user=current_user, db=self.repo.db)
        document = await self.repo.get_detail(kb_id, document_id)
        if document is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="文件不存在")
        storage_key = await self.repo.delete(kb_id, document_id)
        if storage_key is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="文件不存在")

        # 知识库统计自减
        await self.kb_repo.increment_counts(
            kb_id=kb_id, doc_delta=-1, chunk_delta=-document.chunk_count
        )

        # 记录删除成功后再清理物理文件（孤儿文件可容忍，幽灵记录不可）
        await self.storage.delete(storage_key)

    async def download(
            self,
            kb_id: int,
            document_id: int,
            current_user,
    ):
        # 1. 先检查知识库读取权限（先权限后查文档，避免存在性探测）
        await core.permissions.check_knowledge_base_access(
            kb_id=kb_id, current_user=current_user, db=self.repo.db)

        # 2. 查询文档
        document = await self.repo.get_detail(kb_id, document_id)
        if document is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="文件不存在")

        # 3. 检查物理文件是否存在
        file_path = Path(document.storage_key)
        if not file_path.exists():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="文件不存在于存储中")

        # 4. 返回文件流，用原始文件名
        return FileResponse(
            path=str(file_path),
            filename=document.filename,
            media_type=document.mime_type or "application/octet-stream",
        )

    async def preview(self, kb_id: int, document_id: int, current_user):
        # 1. 权限检查
        await core.permissions.check_knowledge_base_access(
            kb_id=kb_id, current_user=current_user, db=self.repo.db)

        # 2. 查询文档
        document = await self.repo.get_detail(kb_id, document_id)
        if document is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="文件不存在")

        # 3. 检查文件类型
        if document.file_type not in PREVIEW_TYPES:
            raise HTTPException(status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE, detail="文件类型不允许预览")

        # 4. 物理文件存在性检查
        file_path = Path(document.storage_key)
        if not file_path.exists():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="文件不存在于存储中")

        # 5. 返回文件流，用原始文件名
        return FileResponse(
            path=str(file_path),
            filename=document.filename,
            media_type=document.mime_type or "application/octet-stream",
            content_disposition_type="inline"
        )