from sqlalchemy import Column, Integer, String
from sqlalchemy.sql.expression import text
from sqlalchemy.sql.sqltypes import TIMESTAMP

from app.core.database import Base


class User(Base):
    __tablename__ = "users"
    id = Column(Integer,primary_key=True,nullable=False)
    email = Column(String(100), nullable=False,unique=True)
    password =Column(String(200),nullable=False)
    created_at =Column(TIMESTAMP(timezone=True),nullable=False,server_default=text('now()'))

