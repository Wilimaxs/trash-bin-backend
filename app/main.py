from contextlib import asynccontextmanager
from importlib import import_module

from fastapi import FastAPI

from app.api import api_router
from app.core.exceptions import include_app_exceptions


@asynccontextmanager
async def lifespan(_app: FastAPI):
    yield


import_module("app.models")

app = FastAPI(title="Trash Bin API", lifespan=lifespan)

include_app_exceptions(app)

app.include_router(api_router)


@app.get("/")
async def root():
    return {"message": "Hello World"}
