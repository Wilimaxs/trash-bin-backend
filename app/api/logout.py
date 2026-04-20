from fastapi import APIRouter, Depends, status
from sqlalchemy import delete
from sqlalchemy.orm import Session

from app.db.deps import get_db
from app.models.user_session import UserSession
from app.models.user import User
from app.schemas.common import success
from app.services.api_header import get_current_user

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post(path="/logout", status_code=status.HTTP_200_OK)
def logout_user(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Logout user by revoking all their sessions (deleting refresh tokens).
    """
    # Delete all session tokens for current user
    db.execute(delete(UserSession).where(UserSession.user_id == current_user.id))
    db.commit()

    return success(message="Logout successful")

