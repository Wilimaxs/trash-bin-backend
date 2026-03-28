from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.user import User
from app.schemas.registration_request import RegistrationRequest
from app.schemas.common import success
from app.services.security import hash_password
from app.db.deps import get_db

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post(path="/registration", status_code=201)
def register_user(payload: RegistrationRequest, db: Session = Depends(get_db)) -> dict:
    """
    Check if email already exists in the database
    """
    existing_email = db.execute(select(User).where(User.email == payload.email)).scalar_one_or_none()
    if existing_email:
        raise HTTPException(status_code=400, detail="Email already registered")

    """
    Make a new user
    """
    user = User(
        email=payload.email,
        password=hash_password(payload.password),
        full_name=payload.full_name,
        total_points=0,
    )

    """
    Save user to the database
    """
    db.add(user)
    db.commit()
    db.refresh(user)

    """
    Return response json
    """
    return success(
        message="Registration successful",
        data={
            "id": user.id,
            "email": user.email,
            "full_name": user.full_name,
            "total_points": user.total_points,
        },
    )
