import enum
from sqlalchemy import Column, Integer, String, Enum
from sqlalchemy.sql.expression import text
from sqlalchemy.sql.sqltypes import TIMESTAMP
from app.core.database import Base


class UserRole(str, enum.Enum):
    user = "user"
    admin = "admin"


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, nullable=False)
    email = Column(String(100), nullable=False, unique=True)
    password = Column(String(200), nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))
    role = Column(Enum(UserRole), default=UserRole.user, nullable=False)


class User_request(Base):
    __tablename__ = "users_request"
    id = Column(Integer, primary_key=True, nullable=False)
    email = Column(String(100), nullable=False)
    reason = Column(String(1000))
    status = Column(String(20))
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))
    approved_at = Column(TIMESTAMP(timezone=True))
    token = Column(String(50))
    # expire_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text("(now() + interval 3 day)"))
    expire_at = Column(TIMESTAMP(timezone=True))
