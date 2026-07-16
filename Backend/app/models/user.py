import enum
from sqlalchemy import Column, Integer, String, Enum, ForeignKey
from sqlalchemy.orm import relationship
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
    # created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))
    # approved_at = Column(TIMESTAMP(timezone=True))
    # expire_at = Column(TIMESTAMP(timezone=True))
    invite_tokens = relationship("InviteToken", back_populates="request")

class InviteToken(Base):
    __tablename__ = "invite_tokens"
    id = Column(Integer, primary_key=True, nullable=False)
    request_id = Column(
        Integer,
        ForeignKey("users_request.id", ondelete="CASCADE"),
        nullable=False
    )
    email = Column(String(100), nullable=False)
    token_hash = Column(String(255))
    expire_at = Column(TIMESTAMP(timezone=True))
    used_at = Column(TIMESTAMP(timezone=True))
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))
    request = relationship("User_request", back_populates="invite_tokens")