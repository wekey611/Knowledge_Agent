from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import declarative_base
import app.settings

DB_URI = app.settings.DB_URI

engine = create_async_engine(DB_URI)

SessionLocal = async_sessionmaker(autocommit=False, autoflush=False, bind=engine, class_=AsyncSession)
Base = declarative_base()


async def close_db_engine():
    """关闭数据库引擎，释放所有连接池中的连接。

    必须在事件循环关闭之前调用（在 asyncio.run 的协程内）。
    - FastAPI 应用：在 lifespan shutdown 中调用
    - 独立脚本：在 async 函数的末尾调用
    """
    await engine.dispose()


async def get_db():
    async with SessionLocal() as db:
        try:
            yield db
        finally:
            await db.close()
