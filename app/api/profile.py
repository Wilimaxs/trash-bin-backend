from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.db.deps import get_db
from app.models.disposal_history import DisposalHistory
from app.models.user import User
from app.schemas.common import success
from app.schemas.update_profile_request import UpdateProfileRequest
from app.services.api_header import get_current_user

router = APIRouter(prefix="/user", tags=["user"])


@router.get("/profile")
def get_user_profile(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Menghitung total items (jumlah histori buang sampah user ini)
    count_query = select(func.count()).select_from(DisposalHistory).where(DisposalHistory.user_id == current_user.id)
    total_items = db.scalar(count_query) or 0

    # Mengambil tahun dari kolom created_at untuk UI "Member since 2023"
    member_since_year = current_user.created_at.strftime("%Y") if current_user.created_at else "2024"

    return success(
        message="Success retrieve user profile",
        data={
            "full_name": current_user.full_name,
            "email": current_user.email,
            "avatar_url": current_user.avatar_url,
            "member_since": f"Member since {member_since_year}",
            "total_points": current_user.total_points,
            "total_items": total_items
        }
    )


@router.put("/profile")
def update_user_profile(
    payload: UpdateProfileRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if payload.full_name is not None:
        current_user.full_name = payload.full_name

    if payload.avatar_url is not None:
        current_user.avatar_url = payload.avatar_url

    db.commit()
    db.refresh(current_user)

    return success(
        message="Profile updated successfully",
        data={
            "id": current_user.id,
            "full_name": current_user.full_name,
            "email": current_user.email,
            "avatar_url": current_user.avatar_url
        }
    )
