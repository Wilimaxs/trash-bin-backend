from fastapi import APIRouter
from app.api.registration import router as registration_router
from app.api.verify import router as verify_router
from app.api.login import router as login_router

api_router = APIRouter()
api_router.include_router(registration_router)
api_router.include_router(verify_router)
api_router.include_router(login_router)
