from typing import Optional

from pydantic import BaseModel
from datetime import datetime
from app import schemas

class OrganizationCreate(BaseModel):
    name: str
    description: str

class OrganizationUpdate(BaseModel):
    name: str
    description: str

class OrganizationOut(BaseModel):
    id: int
    name: str
    description: str
    created_at: datetime
    model_config = {"from_attributes": True}


class OrganizationMemberOut(BaseModel):
    role: str
    joined_at: datetime
    user: Optional[schemas.user.UserOut] = None

    model_config = {"from_attributes": True}

class OrganizationDetail(BaseModel):
    id: int
    name: str
    description: str
    created_at: datetime

    owner:Optional[schemas.user.UserOut] = None
    members:Optional[list[OrganizationMemberOut]] = None
    model_config = {"from_attributes": True}


class OrganizationMemberCreate(BaseModel):
    user_id: int
    role: str

class OrganizationMemberUpdate(BaseModel):
    role: str
