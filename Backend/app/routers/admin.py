from fastapi import APIRouter, status, Depends, Path, BackgroundTasks
from app import repositories, core
from app.core.database import get_db, AsyncSession

router = APIRouter(
    prefix="/admin",
    tags=["admin"]
)


@router.post("/{request_id}/approve", status_code=status.HTTP_200_OK)
async def approve_request(
        background_tasks: BackgroundTasks,
        request_id=Path(...),
        user=Depends(core.oauth2.require_admin),
        db: AsyncSession = Depends(get_db)
):
    repo = repositories.request.RequestRepository(db)
    result = await repo.approve(request_id)

    background_tasks.add_task(
        core.mail.send_approve_email,
        email=result["email"],
        register_url=result["register_url"]
    )
    return result
