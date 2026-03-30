from fastapi import APIRouter
from app.api.registration import router as registration_router
from app.api.verify import router as verify_router
from app.api.login import router as login_router
from app.api.forgot_password import router as forgot_password_router
from app.api.reset_password import router as reset_password_router
from app.api.history import router as history_router
from app.api.point_earned import router as point_earned_router
from app.api.profile import router as profile_router


api_router = APIRouter()
api_router.include_router(registration_router)
api_router.include_router(verify_router)
api_router.include_router(login_router)
api_router.include_router(forgot_password_router)
api_router.include_router(reset_password_router)
api_router.include_router(history_router)
api_router.include_router(point_earned_router)
api_router.include_router(profile_router)
