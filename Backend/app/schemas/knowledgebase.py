from datetime import datetime
from pydantic import BaseModel
from typing import Optional

from app import models, schemas


class KnowledgeBase(BaseModel):
    name: str
    description: str | None = None
    scope: models.knowledge.KnowledgeSource
    chunk_size: int = 500
    chunk_overlap: int = 50
    org_id: int | None = None


class KnowledgeBaseCreate(KnowledgeBase):
    pass


class KnowledgeBaseUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    chunk_size: int | None = None
    chunk_overlap: int | None = None


class KnowledgeBaseSimple(BaseModel):
    id: int
    name: str
    description: str | None = None
    scope: models.knowledge.KnowledgeSource
    status: models.knowledge.KBStatus
    document_count: int
    created_at: datetime


class KnowledgeBaseDetail(KnowledgeBase):
    id: int
    document_count: int
    chunk_count: int
    owner_id: int
    organization: Optional[schemas.organization.OrganizationOut] = None
    status: models.knowledge.KBStatus
    created_at: datetime
    updated_at: datetime


class KnowledgeBaseList(BaseModel):
    total: int
    data: list[KnowledgeBaseSimple]
