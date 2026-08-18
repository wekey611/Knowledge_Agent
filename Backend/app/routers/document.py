from fastapi import APIRouter, status, Depends, Path, UploadFile, File
from app import repositories, core, schemas, models, services
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
