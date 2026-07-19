from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app import schemas, models, core
from starlette import status
import hashlib
from datetime import datetime, timedelta


class UserRepository:
    def __init__(self, db=AsyncSession):
        self.db = db

    # 创建账号
    async def create(self, user_data: schemas.user.UserCreate, hashed_password) -> models.user.User:
        new_user = models.user.User(**user_data.dict(exclude={"password"}), password=hashed_password)
        self.db.add(new_user)
        await self.db.commit()
        await self.db.refresh(new_user)
        return new_user

    # 登录账号
    async def login(self, user_credentials):
        stmt = select(models.user.User).where(models.user.User.email == user_credentials.username)
        result = await self.db.execute(stmt)
        user = result.scalar_one_or_none()

        if not user:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid Credentials")

        if not core.security.verify_password(user_credentials.password, user.password):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid Credentials")

        # create token
        access_token = await core.oauth2.create_access_token(data={"user_id": user.id})

        return access_token

    async def get_invite_info(self, token: str) -> schemas.user.InviteTokenInfoOut:
        """查询 token 信息"""
        token_hash = hashlib.sha256(token.encode()).hexdigest()
        stmt = select(models.user.InviteToken).where(models.user.InviteToken.token_hash == token_hash)
        result = await self.db.execute(stmt)
        invite = result.scalar_one_or_none()

        if invite is None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="无效的链接")

        return schemas.user.InviteTokenInfoOut(
            email=invite.email,
            expired=invite.expire_at < datetime.utcnow(),
            used=invite.used_at is not None,
        )

    async def register(self, token, password):
        token_hash = hashlib.sha256(token.encode()).hexdigest()

        stmt = select(models.user.InviteToken).where(models.user.InviteToken.token_hash == token_hash)
        result = await self.db.execute(stmt)
        invite = result.scalar_one_or_none()

        if invite is None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="无效的链接")

        if invite.expire_at < datetime.utcnow():
            req_stmt = select(models.user.User_request).where(models.user.User_request.id == invite.request_id)
            req_result = await self.db.execute(req_stmt)
            req = req_result.scalar_one_or_none()
            if req:
                req.status = "expired"
            await self.db.commit()
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="链接已过期")

        if invite.used_at is not None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="该链接已被使用")

        user_stmt = select(models.user.User).where(models.user.User.email == invite.email)
        user_result = await self.db.execute(user_stmt)
        user = user_result.scalar_one_or_none()

        if user is not None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="该邮箱已被注册")

        # 标记 token 已使用
        invite.used_at = datetime.utcnow()

        # 更新申请单状态
        req_stmt = select(models.user.User_request).where(
            models.user.User_request.id == invite.request_id
        )
        req_result = await self.db.execute(req_stmt)
        req = req_result.scalar_one_or_none()
        if req:
            req.status = "registered"

        # await self.db.commit()

        hashed_password = core.security.get_password_hash(password)
        user_data = schemas.user.UserCreate(email=invite.email, password=password)
        new_user = await self.create(user_data, hashed_password)

        return new_user
