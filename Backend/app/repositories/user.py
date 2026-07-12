from alembic.util import status
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_
from app import schemas, models, core
from starlette import status


class UserRepository:
    def __init__(self, db=AsyncSession):
        self.db = db

    # 创建账号
    async def create(self, user_data: schemas.user.UserCreate, hashed_password) -> models.user.User:
        new_user = models.user.User(**user_data.dict(exclude={"password"}), password=hashed_password)
        self.db.add(new_user)
        await self.db.commit()
        await  self.db.refresh(new_user)
        return new_user

    # 登录账号
    async def login(self, user_credentials):
        stmt = select(models.user.User).where(models.user.User.email == user_credentials.username)
        result = await  self.db.execute(stmt)
        user = result.scalar_one_or_none()

        if not user:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid Credentials")

        if not core.security.verify_password(user_credentials.password, user.password):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid Credentials")

        # create token
        access_token = await core.oauth2.create_access_token(data={"user_id": user.id})

        return access_token

    # 注册申请
    async def request(self, user: schemas.user.User_Request_In) -> models.user.User_request:
        stmt = select(models.user.User_request).where(models.user.User_request.email == user.email, or_(
            models.user.User_request.status == 'rejected',
            models.user.User_request.status.is_(None)))
        user_request = await self.db.execute(stmt)

        if user_request:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"您已发过申请!")

        new_user_request = models.user.User_request(**user.dict(exclude={"status"}), status="pending")

        self.db.add(new_user_request)
        await self.db.commit()
        await self.db.refresh(new_user_request)
        return new_user_request
