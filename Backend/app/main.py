from fastapi import FastAPI
from app.core.database import engine
from app import routers
from sqladmin import Admin
from app.admin import UserAdmin
from fastapi.responses import FileResponse


app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}

@app.get("/register")
async def register_page():
    return FileResponse("app/static/register.html")

app.include_router(routers.user.router)
app.include_router(routers.auth.router)
app.include_router(routers.admin.router)

admin = Admin(app, engine)
admin.add_view(UserAdmin)