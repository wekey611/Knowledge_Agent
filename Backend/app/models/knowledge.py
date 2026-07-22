from sqlalchemy import Column, Integer, String, Enum, ForeignKey, BigInteger, Text, Boolean, UniqueConstraint, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql.expression import text
from sqlalchemy.sql.sqltypes import TIMESTAMP
from app.core.database import Base


class KnowledgeBase(Base):
    __tablename__ = "knowledge_base"
    __table_args__ = (
        Index("idx_scope", "scope"),
        Index("idx_owner", "owner_id"),
        Index("idx_org", "org_id"),
        {"comment": "知识库主表"}
    )

    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="知识库唯一ID")
    name = Column(String(100), nullable=False, comment="知识库名称")
    description = Column(Text, nullable=True, comment="知识库描述")
    scope = Column(String(20), nullable=False, comment="可见范围: public-公开, org-组织内, personal-个人")
    owner_id = Column(BigInteger, ForeignKey("users.id"), nullable=False, comment="创建者用户ID")
    org_id = Column(BigInteger, ForeignKey("organization.id"), nullable=True, comment="所属组织ID, 个人知识库为空")
    embedding_model = Column(String(100), nullable=True, comment="向量化模型名称, 如 text-embedding-3-small")
    vector_store = Column(String(100), nullable=True, comment="向量存储类型, 如 chroma/pgvector")
    document_count = Column(Integer, default=0, comment="文档总数统计")
    chunk_count = Column(Integer, default=0, comment="分块总数统计")
    status = Column(String(20), default="ready", comment="状态: building-构建中, ready-就绪, failed-构建失败")
    created_at = Column(TIMESTAMP(timezone=True), server_default=text('now()'), comment="创建时间")
    updated_at = Column(TIMESTAMP(timezone=True), server_default=text('now()'), onupdate=text('now()'),
                        comment="更新时间")
    deleted = Column(Boolean, default=False, comment="软删除标记: 0-未删除, 1-已删除")

    # 关系
    owner = relationship("User", back_populates="knowledge_bases", lazy="selectin")
    organization = relationship("Organization", back_populates="knowledge_bases", lazy="selectin")
    documents = relationship("Document", back_populates="knowledge_base", cascade="all, delete-orphan")


class Document(Base):
    __tablename__ = "document"
    __table_args__ = (
        Index("idx_kb", "kb_id"),
        Index("idx_uploader", "uploader_id"),
        Index("idx_status", "parser_status"),
        {"comment": "文档表"}
    )

    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="文档ID")
    kb_id = Column(BigInteger, ForeignKey("knowledge_base.id", ondelete="CASCADE"), nullable=False,
                   comment="所属知识库")
    uploader_id = Column(BigInteger, ForeignKey("users.id"), nullable=False, comment="上传用户")
    title = Column(String(255), nullable=False, comment="文档标题")
    filename = Column(String(255), nullable=False, comment="原始文件名")
    file_type = Column(String(20), nullable=False, comment="pdf/docx/md/txt/html")
    mime_type = Column(String(100), nullable=True, comment="application/pdf")
    file_size = Column(BigInteger, nullable=False, comment="文件大小(Byte)")
    storage_path = Column(String(500), nullable=False, comment="服务器存储路径")
    parser_status = Column(String(20), default="waiting", comment="waiting/parsing/embedding/completed/failed")
    chunk_count = Column(Integer, default=0, comment="切块数量")
    remark = Column(String(500), nullable=True, comment="失败原因或备注")
    created_at = Column(TIMESTAMP(timezone=True), server_default=text('now()'), comment="创建时间")
    updated_at = Column(TIMESTAMP(timezone=True), server_default=text('now()'), onupdate=text('now()'),comment="更新时间")
    deleted = Column(Boolean, default=False, comment="逻辑删除")

    # 关系
    knowledge_base = relationship("KnowledgeBase", back_populates="documents", lazy="selectin")
    uploader = relationship("User", back_populates="documents", lazy="selectin")
    chunks = relationship("Chunk", back_populates="document", cascade="all, delete-orphan")

    class Chunk(Base):
        __tablename__ = "chunk"
        __table_args__ = (
            Index("idx_document", "document_id"),
            {"comment": "文档分块表"}
        )

        id = Column(BigInteger, primary_key=True, autoincrement=True, comment="分块唯一ID")
        document_id = Column(BigInteger, ForeignKey("document.id", ondelete="CASCADE"), nullable=False,
                             comment="所属文档ID")
        chunk_index = Column(Integer, nullable=True, comment="分块序号(从0开始)")
        content = Column(Text, nullable=True, comment="分块文本内容")  # LONGTEXT 对应 Text
        token_count = Column(Integer, default=0, comment="Token数量估算")
        vector_id = Column(String(255), nullable=True, comment="向量数据库中的向量ID")
        created_at = Column(TIMESTAMP(timezone=True), server_default=text('now()'), comment="创建时间")

        # 关系
        document = relationship("Document", back_populates="chunks")
