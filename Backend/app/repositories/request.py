import hashlib
import secrets
from datetime import datetime, timedelta
from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
from app import models, schemas, settings


class RequestRepository:
    def __init__(self, db=AsyncSession):
        self.db = db

    async def get_by_id(self, request_id: int):
        stmt = select(models.user.User_request).where(models.user.User_request.id == request_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    # 注册申请
    async def request(self, user: schemas.user.User_Request_In) -> models.user.User_request:
        stmt = select(models.user.User_request).where(
            models.user.User_request.email == user.email,
            models.user.User_request.status.in_(['pending', 'approved', 'registered']))

        result = await self.db.execute(stmt)
        existing = result.scalars().first()

        if existing is not None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"您已发过申请!")

        new_user_request = models.user.User_request(**user.dict(exclude={"status"}), status="pending")

        self.db.add(new_user_request)
        await self.db.commit()
        await self.db.refresh(new_user_request)
        return new_user_request

    async def get_all(self):
        stmt = select(models.user.User_request)
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def approve(self, request_id: int):
        req = await self.get_by_id(request_id)

        if req is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="申请不存在")

        if req.status != "pending":
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="该申请已被处理")

        req.status = "approved"

        new_token = secrets.token_urlsafe(32)
        hash_token = hashlib.sha256(new_token.encode()).hexdigest()
        expire_at = datetime.utcnow() + timedelta(days=3)
        user_email = req.email

        invite = models.user.InviteToken(
            request_id=req.id,
            email=user_email,
            token_hash=hash_token,
            created_at= datetime.utcnow(),
            expire_at= expire_at,
        )
        self.db.add(invite)

        await self.db.commit()

        # 邀请链接指向前端注册页（hash 路由）
        register_url = f"{settings.FRONTEND_URL}/#/auth/register?token={new_token}"
        print(register_url)

        return {
            "message": "已接受申请",
            "email": user_email,
            "register_url": register_url,
        }

