from contextlib import asynccontextmanager

from fastapi import FastAPI
from app.core.database import engine, close_db_engine
from app import routers, settings
from sqladmin import Admin
from app.admin import UserAdmin
from app.core.admin_auth import AdminAuth
from fastapi.responses import FileResponse


@asynccontextmanager
async def lifespan(app: FastAPI):
    """FastAPI 应用生命周期管理"""
    yield
    # 关闭数据库引擎,避免事件循环关闭后连接报错
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
app.include_router(routers.rag.router)

# sqladmin 后台挂载独立账号认证(不与用户表耦合)
admin = Admin(
    app,
    engine,
    authentication_backend=AdminAuth(secret_key=settings.SECRET_KEY),
)
admin.add_view(UserAdmin)
