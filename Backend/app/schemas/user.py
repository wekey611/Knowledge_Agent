from datetime import datetime

from pydantic import BaseModel, EmailStr


class UserCreate(BaseModel):
    email: EmailStr
    password: str


class UserOut(BaseModel):
    id: int
    email: EmailStr
    created_at: datetime

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


class User_Register_In(BaseModel):
    token:str
    password:str

class UserRegisterOut(BaseModel):
    id: int
    email: EmailStr
    created_at:datetime

    model_config = {"from_attributes": True}