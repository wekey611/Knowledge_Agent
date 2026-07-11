from fastapi import FastAPI
from app import models
from app.core.database import engine
from app import routers

models.user.Base.metadata.create_all(bind=engine)
app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}

app.include_router(routers.user.router)
app.include_router(routers.auth.router)