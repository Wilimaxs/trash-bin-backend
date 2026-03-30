from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.db.deps import get_db
from app.models.disposal_history import DisposalHistory
from app.models.user import User
from app.schemas.common import success
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
            "avatar_url": current_user.avatar_url,
            "member_since": f"Member since {member_since_year}",
            "total_points": current_user.total_points,
            "total_items": total_items
        }
    )

