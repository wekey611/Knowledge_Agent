from datetime import datetime

from pydantic import BaseModel

from app import models


class DocumentBase(BaseModel):
    title: str
    remark: str | None = None


class DocumentUpdate(BaseModel):
    title: str | None = None
    remark: str | None = None


class DocumentSimple(BaseModel):
    id: int
    title: str
    filename: str
    file_size: int
    parser_status: models.knowledge.ParserStatus
    chunk_count: int
    updated_at: datetime

    model_config = {"from_attributes": True}


class DocumentDetail(DocumentBase):
    id: int
    filename: str
    mime_type: str | None = None
    page_count: int | None = None
    file_hash: str
    chunk_count: int
    parse_duration: int | None = None
    created_at: datetime
    updated_at: datetime


class DocumentList(BaseModel):
    total: int
    data: list[DocumentSimple]