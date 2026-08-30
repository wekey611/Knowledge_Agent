"""
文档索引后台任务。

对接 parser_status 状态机：
    waiting → parsing → embedding → completed
    ↓（失败）
    failed

V2 实现：
    - 使用 FastAPI BackgroundTasks（学习期足够）
    - 生产可换 Celery / ARQ（V5 优化）

依赖：
    rag 模块（独立模块，不依赖 FastAPI/MySQL）
"""
import logging
from pathlib import Path

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import AsyncSessionLocal
from app.models.knowledge import Document, ParserStatus
from rag.config import load_config
from rag.exceptions import IndexingError
from rag.factory import build_indexer

logger = logging.getLogger(__name__)


async def index_document_task(document_id: int, file_path: str, kb_id: int):
    """
    异步索引文档。

    Args:
        document_id: Document 表的主键
        file_path: 文件的绝对路径
        kb_id: 知识库 ID

    状态机推进：
        waiting → parsing → completed（成功）
        waiting → parsing → failed（失败）
    """
    async with AsyncSessionLocal() as db:
        # 1. 更新状态为 parsing
        doc = await _get_document(db, document_id)
        if not doc:
            logger.error(f"文档 {document_id} 不存在")
            return

        doc.parser_status = ParserStatus.PARSING
        await db.commit()

        # 2. 构造 Indexer 并索引
        try:
            config = load_config()
            indexer = build_indexer(config)
            ids = await indexer.index_file(
                file_path=Path(file_path),
                doc_id=document_id,
                kb_id=kb_id,
            )

            # 3. 索引成功 → completed
            doc.parser_status = ParserStatus.COMPLETED
            doc.chunk_count = len(ids)
            await db.commit()
            logger.info(f"文档 {document_id} 索引成功，写入 {len(ids)} chunks")

        except IndexingError as e:
            # 4. 索引失败 → failed
            doc.parser_status = ParserStatus.FAILED
            await db.commit()
            logger.error(f"文档 {document_id} 索引失败: {e}")

        except Exception as e:
            # 其他错误也标记失败
            doc.parser_status = ParserStatus.FAILED
            await db.commit()
            logger.exception(f"文档 {document_id} 索引异常: {e}")


async def _get_document(db: AsyncSession, document_id: int):
    """从 DB 读取 Document 记录。"""
    from sqlalchemy import select

    result = await db.execute(
        select(Document).where(Document.id == document_id)
    )
    return result.scalar_one_or_none()


__all__ = ["index_document_task"]