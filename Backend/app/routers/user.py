from fastapi import Depends, HTTPException, APIRouter
from starlette import status
from app import models
from app.core.database import get_db
from sqlalchemy.orm import Session
from app import schemas, core

router = APIRouter(
    prefix="/user",
    tags=["users"],
)

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.user.UserOut)
def create_user(user: schemas.user.UserCreate, db: Session = Depends(get_db)):
    # hash the password
    hashed_password = core.security.get_password_hash(user.password)
    user.password = hashed_password

    new_user = models.user.User(**user.dict())
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


@router.get("/{id}", response_model=schemas.user.UserOut)
def get_user(id: int, db: Session = Depends(get_db)):
    user = db.query(models.user.User).filter(models.user.User.id == id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User with id {id} not found")
    return user
