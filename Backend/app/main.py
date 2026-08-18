from contextlib import asynccontextmanager

from fastapi import FastAPI
from app.core.database import engine, close_db_engine
from app import routers
from sqladmin import Admin
from app.admin import UserAdmin
from fastapi.responses import FileResponse


@asynccontextmanager
async def lifespan(app: FastAPI):
    """FastAPI 应用生命周期管理"""
    yield
    # 关闭数据库引擎，避免事件循环关闭后连接报错
    await close_db_engine()


app = FastAPI(lifespan=lifespan)


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}


app.include_router(routers.user.router)
app.include_router(routers.auth.router)
app.include_router(routers.admin.router)
app.include_router(routers.organization.router)

app.include_router(routers.knowledgebase.router)
app.include_router(routers.document.router)

admin = Admin(app, engine)
admin.add_view(UserAdmin)
