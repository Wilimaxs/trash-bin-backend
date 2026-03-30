from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy import select, delete
from sqlalchemy.orm import Session

from app.core.config import get_wib_time
from app.models.user import User
from app.models.user_session import UserSession
from app.schemas.reset_password_request import ResetPasswordRequest
from app.schemas.common import success
from app.services.security import verify_reset_token, hash_password
from app.db.deps import get_db

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post(path="/reset-password", status_code=200)
def reset_password(payload: ResetPasswordRequest, db: Session = Depends(get_db)) -> dict:
    """
    Reset the user password using the reset_token provided by OTP verification
    """
    try:
        # Decode the short-lived reset token
        token_data = verify_reset_token(payload.reset_token)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    email = token_data.get("email")
    user = db.execute(select(User).where(User.email == email)).scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    """
    Update the password
    """
    user.password = hash_password(payload.new_password)

    """
    Option 2 Implementation: 
    Smart UX - If the user's email is not verified, doing a password reset via email OTP 
    proves they own the email, so we auto-verify them.
    """
    if user.email_verified_at is None:
        user.email_verified_at = get_wib_time()

    """
    SECURITY: Revoke all existing sessions (kick out from all devices)
    Force user to re-login with the new password
    """
    db.execute(delete(UserSession).where(UserSession.user_id == user.id))

    db.commit()

    return success(message="Password has been reset successfully. You can now login with your new password.")

