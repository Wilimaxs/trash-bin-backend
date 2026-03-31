from contextlib import asynccontextmanager
from importlib import import_module
import os

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.api import api_router
from app.core.exceptions import include_app_exceptions

os.makedirs("public/avatars", exist_ok=True)


@asynccontextmanager
async def lifespan(_app: FastAPI):
    yield


import_module("app.models")

app = FastAPI(title="Trash Bin API", lifespan=lifespan)

app.mount("/public", StaticFiles(directory="public"), name="public")

include_app_exceptions(app)

app.include_router(api_router)


@app.get("/")
async def root():
    return {"message": "Hello World"}
