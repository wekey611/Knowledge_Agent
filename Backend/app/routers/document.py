from fastapi import APIRouter, status, Depends, Path, UploadFile, File
from app import core, schemas, models, services
from app.core.database import get_db, AsyncSession

router = APIRouter(
    prefix="/knowledge-bases",
    tags=["knowledge"]
)


@router.post("/{kb_id}/documents", response_model=schemas.document.DocumentSimple, status_code=status.HTTP_201_CREATED)
async def upload_document(
        kb_id: int = Path(..., description="Knowledge Base ID"),
        current_user: models.user.User = Depends(core.oauth2.get_current_user),
        file: UploadFile = File(...),
        db: AsyncSession = Depends(get_db)
):
    service = services.document.DocumentService(db)
    return await service.upload(kb_id=kb_id, user=current_user, file=file)


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
