from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict


class HistoryItemResponse(BaseModel):
    id: int
    image_url: Optional[str] = None
    points_earned: int
    compartment_type: str
    sub_category: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class HistoryPaginationResponse(BaseModel):
    data: List[HistoryItemResponse]
    total: int
    page: int
    size: int
    total_pages: int

