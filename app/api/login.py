from datetime import timedelta, datetime, timezone
from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy import select, delete
from sqlalchemy.orm import Session

from app.core.config import ACCESS_TOKEN_EXPIRE_MINUTES, REFRESH_TOKEN_EXPIRE_DAYS
from app.models.user import User
from app.models.user_session import UserSession
from app.schemas.login_request import LoginRequest
from app.schemas.common import success
from app.services.security import verify_password, create_access_token, create_refresh_token
from app.db.deps import get_db

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post(path="/login", status_code=status.HTTP_200_OK)
def login_user(payload: LoginRequest, db: Session = Depends(get_db)):
    """
    Authenticate user and return access & refresh tokens
    """
    user = db.execute(select(User).where(User.email == payload.email)).scalar_one_or_none()

    # Check if a user exists and the password is correct
    # noinspection PyTypeChecker
    if not user or not verify_password(payload.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )

    # Check if the user is verified
    if user.email_verified_at is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Email not verified. Please verify your account first."
        )

    # Generate Tokens
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    refresh_token_expires = timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)

    access_token = create_access_token(
        data={"sub": str(user.id)}, expires_delta=access_token_expires
    )
    refresh_token = create_refresh_token(
        data={"sub": str(user.id)}, expires_delta=refresh_token_expires
    )

    # Delete existing sessions to enforce a single device login
    db.execute(delete(UserSession).where(UserSession.user_id == user.id))

    # Store refresh token in database
    # noinspection PyTypeChecker
    new_session = UserSession(
        user_id=user.id,
        refresh_token=refresh_token,
        expires_at=datetime.now(timezone.utc) + refresh_token_expires
    )
    db.add(new_session)
    db.commit()

    return success(
        message="Login successful",
        data={
            "user": {
                "id": user.id,
                "email": user.email,
                "full_name": user.full_name,
                "avatar_url": user.avatar_url,
                "total_points": user.total_points,
            },
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer"
        }
    )
