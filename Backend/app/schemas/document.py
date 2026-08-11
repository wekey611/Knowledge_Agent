from datetime import datetime
from pydantic import BaseModel
from typing import Optional

from app import models, schemas

class DocumentBase(BaseModel):
    title: str
    remaker: str


class DocumentUpdate(DocumentBase):
    pass

class DocumentSimple(BaseModel):
    id: int
    title: str
    filename: str
    file_size: int
    parser_status: models.knowledge.ParserStatus
    chunk_count: int
    updated_at: datetime

class DoucumentDetail(DocumentBase):
    id: int
    title: str
    filename: str
    mime_type: str
    page_count: int
    file_hash: str
    chunk_count: int
    parse_duration: int
    remark: str
    created_at: datetime

class DocumentList(BaseModel):
    total: int
    data: list[DocumentSimple]