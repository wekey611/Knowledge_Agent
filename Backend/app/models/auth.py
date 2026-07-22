import enum
from sqlalchemy import Column, Integer, String, Enum, ForeignKey, BigInteger, Text, Boolean, UniqueConstraint, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql.expression import text
from sqlalchemy.sql.sqltypes import TIMESTAMP
from app.core.database import Base

class OrganizationRole(str,enum.Enum):
    OWNER = "owner"
    ADMIN = "admin"
    MEMBER = "member"


class Organization(Base):
    __tablename__ = "organization"
    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True, comment="组织ID")
    name = Column(String(100), nullable=False, comment="组织名称")
    description = Column(Text, nullable=True, comment="组织描述")
    owner_id = Column(BigInteger, ForeignKey("users.id"), nullable=False, comment="创建人")
    avatar = Column(String(255), nullable=True, comment="头像")
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'), comment="创建时间")
    updated_at = Column(TIMESTAMP, server_default=text('now()'), onupdate=text('now()'), comment="更新时间")
    deleted = Column(Boolean, default=False, comment="软删除标记")

    # 关系
    owner = relationship("User", back_populates="organizations", lazy="selectin")
    members = relationship("OrganizationMember", back_populates="organization", lazy="selectin")
    knowledge_bases = relationship("KnowledgeBase", back_populates="organization", cascade="all, delete-orphan")

class OrganizationMember(Base):
    __tablename__ = "organization_member"
    # 联合唯一约束
    __table_args__ = (
        UniqueConstraint("org_id", "user_id", name="uk_org_user"),
        Index("idx_user", "user_id"),
    )

    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="成员ID")
    org_id = Column(BigInteger, ForeignKey("organization.id", ondelete="CASCADE"), nullable=False, comment="组织ID")
    user_id = Column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, comment="用户ID")
    role = Column(Enum(OrganizationRole), nullable=False, default=OrganizationRole.MEMBER, comment="角色: owner/admin/member")
    joined_at = Column(TIMESTAMP(timezone=True), server_default=text('now()'), comment="加入时间")

    # 关系
    organization = relationship("Organization", back_populates="members", lazy="selectin")
    user = relationship("User", back_populates="organization_members", lazy="selectin")


