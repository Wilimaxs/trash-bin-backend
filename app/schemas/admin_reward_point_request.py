from typing import Optional

from pydantic import BaseModel


class BaseRewardPoint(BaseModel):
    compartment_type: str
    sub_category: Optional[str] = None
    reward_points: int

class RewardPointCreate(BaseRewardPoint):
    pass

class RewardPointResponse(BaseRewardPoint):
    id: int

    class Config:
        from_attributes = True