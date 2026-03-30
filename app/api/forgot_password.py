import random
import resend
from datetime import timedelta
from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import OTP_TOKEN_EXPIRE_MINUTES, RESEND_API_KEY
from app.models.user import User
from app.schemas.forgot_password_request import ForgotPasswordRequest
from app.schemas.common import success
from app.services.security import create_otp_token
from app.db.deps import get_db
from app.utils.email_forgot_templates import get_otp_forgot_password_html

resend.api_key = RESEND_API_KEY

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post(path="/forgot-password", status_code=200)
def forgot_password_request(payload: ForgotPasswordRequest, db: Session = Depends(get_db)) -> dict:
    """
    Send OTP code to user's email to reset password 
    """
    # noinspection PyTypeChecker
    user = db.execute(select(User).where(User.email == payload.email)).scalar_one_or_none()

    # Generate OTP
    otp_code = str(random.randint(a=100000, b=999999))
    expires = timedelta(minutes=OTP_TOKEN_EXPIRE_MINUTES)
    token = create_otp_token(email=str(payload.email), otp_code=otp_code, expires_delta=expires)

    # Only send email if the user exists
    if user:
        try:
            if RESEND_API_KEY:
                # noinspection PyTypeChecker
                params: resend.Emails.SendParams = {
                    "from": "Trash Bin App <no-reply@notify.basehub.me>",
                    "to": [user.email],
                    "subject": "Reset Password - Trash Bin API",
                    "html": get_otp_forgot_password_html(otp_code),
                } # type: ignore
                resend.Emails.send(params)
        except Exception as e:
            print("Failed to send email", str(e))

    # General response for forgot password request
    return success(
        message="If your email is registered, you will receive an OTP code to reset your password.",
        data={
            "access_token": token,
        },
    )
