from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from starlette import status
from app.core.database import get_db, AsyncSession
from app import schemas, models, core, repositories

router = APIRouter(tags=["Authentication"])


@router.post('/login', response_model=schemas.auth.Token)
async def login(user_credentials: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    repo = repositories.user.UserRepository(db)

    return {"access_token": await repo.login(user_credentials), "token_type": "bearer"}

@router.get("/admin/requests")
async def list_all_requests(user=Depends(core.permissions.require_admin),db:AsyncSession=Depends(get_db)):
    repo =repositories.request.RequestRepository(db)
    return await repo.get_all()

@router.get("/me",response_model=schemas.user.UserOut)
async def read_users_me(current_user: models.user.User = Depends(core.permissions.get_current_user)):
    return current_user
