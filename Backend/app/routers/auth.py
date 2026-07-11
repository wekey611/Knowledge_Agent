from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from starlette import status

from app import schemas, models, core
from app.core.database import get_db

router = APIRouter(tags=["Authentication"])


@router.post('/login',response_model=schemas.auth.Token)
def login(user_credentials: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db),):
    user = db.query(models.user.User).filter(models.user.User.email == user_credentials.username).first()

    if not user:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid Credentials")

    if not core.security.verify_password(user_credentials.password, user.password):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid Credentials")

    # create token
    access_token = core.oauth2.create_access_token(data={"user_id": user.id})

    return {"access_token": access_token, "token_type": "bearer"}

@router.get('/get_user')
def get_user(
    db: Session = Depends(get_db),  # ✅ 去掉括号
    # current_user_data: schemas.auth.TokenData = Depends(core.oauth2.get_current_user)
    current_user:int=Depends(core.oauth2.get_current_user)
):
    print(current_user.id)
    # # 使用 current_user_data.id 来查询用户
    # user = db.query(models.user.User).filter(
    #     models.user.User.id == current_user.id
    # ).first()
    # if not user:
    #     raise HTTPException(
    #         status_code=status.HTTP_403_FORBIDDEN,
    #         detail="User not found"
    #     )
    return