import math
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy import desc, func, select
from sqlalchemy.orm import Session

from app.db.deps import get_db
from app.models.disposal_history import DisposalHistory
from app.models.trash_category import TrashCategory
from app.models.user import User
from app.schemas.common import success
from app.schemas.history_response import HistoryItemResponse, HistoryPaginationResponse
from app.services.api_header import get_current_user

router = APIRouter(prefix="/history", tags=["history"])


@router.get("")
def get_user_history(
    compartment_type: Optional[str] = Query(None, alias="type", description="Filter by compartment type (organic, inorganic, b3)"),
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(20, ge=1, le=100, description="Items per page"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    offset_val = (page - 1) * size

    # Base query for joined rows (DisposalHistory & TrashCategory)
    query = select(DisposalHistory).join(
        TrashCategory, DisposalHistory.trash_category_id == TrashCategory.id
    ).where(DisposalHistory.user_id == current_user.id)

    # Filter by type if provided and not "all"
    if compartment_type and compartment_type.lower() != "all":
        query = query.where(TrashCategory.compartment_type == compartment_type.lower())

    # Total items count
    count_query = select(func.count()).select_from(query.subquery())
    total_items = db.scalar(count_query) or 0
    total_pages = math.ceil(total_items / size) if total_items > 0 else 0

    # Paginated and sorted data
    items_query = query.order_by(desc(DisposalHistory.created_at)).offset(offset_val).limit(size)
    results = db.scalars(items_query).all()

    # Build response model
    history_items = []
    for hist in results:
        history_items.append(
            HistoryItemResponse(
                id=hist.id,
                image_url=hist.image_url,
                points_earned=hist.points_earned,
                compartment_type=hist.trash_category.compartment_type,
                sub_category=hist.trash_category.sub_category,
                created_at=hist.created_at
            )
        )

    pagination_data = HistoryPaginationResponse(
        data=history_items,
        total=total_items,
        page=page,
        size=size,
        total_pages=total_pages
    )

    return success(
        message="Success retrieve user history",
        data=pagination_data.model_dump()
    )
