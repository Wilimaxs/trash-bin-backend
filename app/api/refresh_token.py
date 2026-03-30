from datetime import timedelta
from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import ACCESS_TOKEN_EXPIRE_MINUTES
from app.db.deps import get_db
from app.models.user_session import UserSession
from app.schemas.refresh_token_request import RefreshTokenRequest
from app.schemas.common import success
from app.services.security import create_access_token, verify_refresh_token

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/refresh-token", status_code=status.HTTP_200_OK)
def refresh_access_token(payload: RefreshTokenRequest, db: Session = Depends(get_db)):
    """
    Get a new access token using a valid refresh token.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired refresh token",
    )

    try:
        user_id = verify_refresh_token(payload.refresh_token)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
        )

    session_record = db.scalar(
        select(UserSession).where(
            UserSession.refresh_token == payload.refresh_token,
            UserSession.user_id == int(user_id)
        )
    )

    if not session_record:
        raise credentials_exception

    # Token is valid, generate a new Access Token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    new_access_token = create_access_token(
        data={"sub": str(user_id)}, expires_delta=access_token_expires
    )

    return success(
        message="Token refreshed successfully",
        data={
            "access_token": new_access_token,
            "refresh_token": payload.refresh_token,
            "token_type": "bearer"
        }
    )
