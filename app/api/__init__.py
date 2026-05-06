from fastapi import APIRouter

from app.api.registration import router as registration_router
from app.api.verify import router as verify_router
from app.api.login import router as login_router
from app.api.logout import router as logout_router
from app.api.forgot_password import router as forgot_password_router
from app.api.reset_password import router as reset_password_router
from app.api.history import router as history_router
from app.api.point_earned import router as point_earned_router
from app.api.profile import router as profile_router
from app.api.bin_session import router as bin_session_router
from app.api.iot import router as iot_router
from app.api.stream import router as stream_router
from app.api.refresh_token import router as refresh_token_router
from app.api.admin_reward_point import router as admin_reward_point_router
from app.api.admin_device import router as admin_device_router
from app.api.admin_upload_model import router as admin_upload_model_router


api_router = APIRouter()
api_router.include_router(registration_router)
api_router.include_router(verify_router)
api_router.include_router(login_router)
api_router.include_router(logout_router)
api_router.include_router(forgot_password_router)
api_router.include_router(reset_password_router)
api_router.include_router(history_router)
api_router.include_router(point_earned_router)
api_router.include_router(profile_router)
api_router.include_router(bin_session_router)
api_router.include_router(iot_router)
api_router.include_router(stream_router)
api_router.include_router(refresh_token_router)
api_router.include_router(admin_reward_point_router)
api_router.include_router(admin_device_router)
api_router.include_router(admin_upload_model_router)
