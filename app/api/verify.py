from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.user import User
from app.schemas.verify_otp_request import VerifyOTPRequest
from app.schemas.common import success
from app.services.security import verify_otp_token
from app.db.deps import get_db

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post(path="/verify", status_code=200)
def verify_otp(payload: VerifyOTPRequest, db: Session = Depends(get_db)) -> dict:
    """
    Verify the OTP code using the provided access token
    """
    try:
        # Decode token to check expiration and get payload
        token_data = verify_otp_token(payload.access_token)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    # Check if the OTP matches
    if token_data.get("otp_code") != payload.otp_code:
        raise HTTPException(status_code=400, detail="Invalid OTP code")

    # Find the user by email extracted from token
    email = token_data.get("email")
    user = db.execute(select(User).where(User.email == email)).scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if user.email_verified_at is not None:
        raise HTTPException(status_code=400, detail="User already verified")

    """
    Update the user verified_at column
    """
    user.email_verified_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(user)

    return success(message="Account successfully verified. You can now login.")

