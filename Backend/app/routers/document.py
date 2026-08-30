from fastapi import APIRouter, status, Depends, Path, UploadFile, File, BackgroundTasks
from app import core, schemas, models, services
from app.core.database import get_db, AsyncSession
from app.tasks.index_tasks import index_document_task

router = APIRouter(
    prefix="/knowledge-bases",
    tags=["knowledge"]
)


@router.post("/{kb_id}/documents", response_model=schemas.document.DocumentSimple, status_code=status.HTTP_201_CREATED)
async def upload_document(
        kb_id: int = Path(..., description="Knowledge Base ID"),
        current_user: models.user.User = Depends(core.oauth2.get_current_user),
        file: UploadFile = File(...),
        background_tasks: BackgroundTasks = BackgroundTasks(),  # V2 新增
        db: AsyncSession = Depends(get_db)
):
    service = services.document.DocumentService(db)
    doc = await service.upload(kb_id=kb_id, user=current_user, file=file)

    # V2 新增：上传成功后触发后台索引任务
    background_tasks.add_task(
        index_document_task,
        document_id=doc.id,
        file_path=doc.storage_key,  # Document 表存的文件路径
        kb_id=kb_id,
    )

    return doc


@router.get("/{kb_id}/documents", response_model=schemas.document.DocumentList, status_code=status.HTTP_200_OK)
async def get_list(
        kb_id: int = Path(..., description="Knowledge Base ID"),
        current_user: models.user.User = Depends(core.oauth2.get_current_user),
        db: AsyncSession = Depends(get_db)
):
    service = services.document.DocumentService(db)
    return await service.get_list(kb_id=kb_id, current_user=current_user)


@router.get("/{kb_id}/documents/{document_id}", response_model=schemas.document.DocumentDetail,
            status_code=status.HTTP_200_OK)
async def get_detail(
        kb_id: int = Path(..., description="Knowledge Base ID"),
        document_id: int = Path(..., description="Document ID"),
        current_user: models.user.User = Depends(core.oauth2.get_current_user),
        db: AsyncSession = Depends(get_db)
):
    service = services.document.DocumentService(db)
    return await service.get_detail(kb_id=kb_id, document_id=document_id, current_user=current_user)


@router.delete("/{kb_id}/documents/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(
        kb_id: int = Path(..., description="Knowledge Base ID"),
        document_id: int = Path(..., description="Document ID"),
        current_user: models.user.User = Depends(core.oauth2.get_current_user),
        db: AsyncSession = Depends(get_db)
):
    service = services.document.DocumentService(db)
    await service.delete(kb_id=kb_id, document_id=document_id, current_user=current_user)


@router.get("/{kb_id}/documents/{document_id}/download", status_code=status.HTTP_200_OK)
async def download_document(
        kb_id: int = Path(..., description="Knowledge Base ID"),
        document_id: int = Path(..., description="Document ID"),
        current_user: models.user.User = Depends(core.oauth2.get_current_user),
        db: AsyncSession = Depends(get_db)
):
    service = services.document.DocumentService(db)
    return await service.download(kb_id=kb_id, document_id=document_id, current_user=current_user)

@router.get("/{kb_id}/documents/{document_id}/preview", status_code=status.HTTP_200_OK)
async def preview_document(
        kb_id: int = Path(..., description="Knowledge Base ID"),
        document_id: int = Path(..., description="Document ID"),
        current_user: models.user.User = Depends(core.oauth2.get_current_user),
        db: AsyncSession = Depends(get_db)
):
    service = services.document.DocumentService(db)
    return await service.preview(kb_id=kb_id, document_id=document_id, current_user=current_user)


