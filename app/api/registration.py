import random
import resend
from datetime import timedelta
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import OTP_TOKEN_EXPIRE_MINUTES, RESEND_API_KEY
from app.models.user import User
from app.schemas.registration_request import RegistrationRequest
from app.schemas.common import success
from app.services.security import hash_password, create_otp_token
from app.db.deps import get_db
from app.utils.email_templates import get_otp_registration_html

resend.api_key = RESEND_API_KEY

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post(path="/registration", status_code=201)
def register_user(payload: RegistrationRequest, db: Session = Depends(get_db)) -> dict:
    """
    Check if email already exists in the database
    """
    # noinspection PyTypeChecker
    existing_email = db.execute(select(User).where(User.email == payload.email)).scalar_one_or_none()
    if existing_email:
        raise HTTPException(status_code=400, detail="Email already registered")

    """
    Make a new user
    """
    # noinspection PyTypeChecker
    user = User(
        email=payload.email,
        password=hash_password(payload.password),
        full_name=payload.full_name,
    )

    """
    Save user to the database
    """
    db.add(user)
    db.commit()
    db.refresh(user)

    """
    Generate OTP and Token
    """
    otp_code = str(random.randint(a=100000, b=999999))
    expires = timedelta(minutes=OTP_TOKEN_EXPIRE_MINUTES)
    token = create_otp_token(email=str(user.email), otp_code=otp_code, expires_delta=expires, token_type="registration")

    try:
        if RESEND_API_KEY:
            # noinspection PyTypeChecker
            params: resend.Emails.SendParams = {
                "from": "Trash Bin App <no-reply@notify.basehub.me>",
                "to": [user.email],
                "subject": "OTP Verification - Trash Bin API",
                "html": get_otp_registration_html(otp_code),
            } # type: ignore
            resend.Emails.send(params)
    except Exception as e:
        print("Failed to send email", str(e))

    """
    Return response json
    """
    return success(
        message="Registration successful. Check your email for OTP.",
        data={
            "access_token": token,
        },
    )
