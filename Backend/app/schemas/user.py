from datetime import datetime

from pydantic import BaseModel, EmailStr


class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str


class UserOut(BaseModel):
    id: int
    username: str
    # NOTE: 用 str 而不是 EmailStr，因为：
    # 1) 数据库里可能存了 .local / .test 等 RFC2606 保留域名
    #    （如 ragbot@test.local 测试用户），pydantic EmailStr 会拒
    # 2) /me 校验失败会让前端拿不到 user.id，导致所有权限判断（canManage）失效
    email: str

    model_config = {"from_attributes": True}


class User_Request_In(BaseModel):
    email: EmailStr
    reason: str


class UserRequestOut(BaseModel):
    id: int
    email: EmailStr
    reason: str | None = None
    status: str | None = None

    model_config = {"from_attributes": True}


class InviteTokenInfoOut(BaseModel):
    email: EmailStr
    expired: bool = False
    used: bool = False


class User_Register_In(BaseModel):
    token: str
    username: str
    password: str


class UserRegisterOut(BaseModel):
    id: int
    email: EmailStr
    created_at: datetime

    model_config = {"from_attributes": True}
