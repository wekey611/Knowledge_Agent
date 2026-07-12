from fastapi import Depends, HTTPException, APIRouter
from starlette import status
from app import models
from app.core.database import get_db, AsyncSession
from app import schemas, core, repositories

router = APIRouter(
    prefix="/user",
    tags=["users"],
)


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.user.UserOut)
async def create_user(user: schemas.user.UserCreate, db: AsyncSession = Depends(get_db)):
    # hash the password
    hashed_password = core.security.get_password_hash(user.password)
    repo = repositories.user.UserRepository(db)
    return await repo.create(user, hashed_password)


@router.get("/{id}", response_model=schemas.user.UserOut)
def get_user(id: int, db: AsyncSession = Depends(get_db)):
    user = db.query(models.user.User).filter(models.user.User.id == id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User with id {id} not found")
    return user


@router.post("/request", status_code=status.HTTP_201_CREATED, response_model=schemas.user.UserOut)
async def user_request(user: schemas.user.User_Request_In, db: AsyncSession = Depends(get_db)):
    repo = repositories.user.UserRepository(db)
    return await repo.request(user)
