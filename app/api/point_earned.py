from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.config import get_wib_time
from app.db.deps import get_db
from app.models.disposal_history import DisposalHistory
from app.models.user import User
from app.schemas.common import success
from app.services.api_header import get_current_user

router = APIRouter(prefix="/history", tags=["history"])

@router.get("/point-earned")
def get_today_point_earned(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    now_wib = get_wib_time()
    start_of_today = now_wib.replace(hour=0, minute=0, second=0, microsecond=0)
    end_of_today = now_wib.replace(hour=23, minute=59, second=59, microsecond=999999)
    
    query = select(func.sum(DisposalHistory.points_earned)).where(
        DisposalHistory.user_id == current_user.id,
        DisposalHistory.created_at >= start_of_today,
        DisposalHistory.created_at <= end_of_today
    )
    
    total_points = db.scalar(query) or 0

    return success(
        message="Success retrieve today's point earned",
        data={"point_earned": total_points}
    )
