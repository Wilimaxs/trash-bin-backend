from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.db.deps import get_db
from app.models import TrashCategory

from app.schemas.admin_reward_point_request import RewardPointResponse, RewardPointCreate
from app.schemas.common import success, error, info

router = APIRouter(prefix="/admin/reward-point", tags=["admin"])

@router.get("/")
def get_reward_point(
        db: Session = Depends(get_db)
):
    records = db.execute(select(TrashCategory)).scalars().all()
    data = [RewardPointResponse.model_validate(r).model_dump() for r in records]
    return success(message="Success retrieve Reward Settings", data=data)


@router.post('/')
def create_reward_point(
        reward_point: RewardPointCreate,
        db: Session = Depends(get_db)
):
    new_reward = TrashCategory(**reward_point.model_dump())
    db.add(new_reward)
    db.commit()
    db.refresh(new_reward)

    data = RewardPointResponse.model_validate(new_reward).model_dump()
    return success(message="Reward successfully added", data=data)

@router.put('/{reward_id}')
def update_reward_point(
        reward_id: int,
        reward_point: RewardPointCreate,
        db: Session = Depends(get_db)
):
    reward = db.execute(select(TrashCategory).where(TrashCategory.id == reward_id)).scalar_one_or_none()
    if not reward:
        return error(message="Reward not found", data=None)

    for key, value in reward_point.model_dump().items():
        setattr(reward, key, value)

    db.commit()
    db.refresh(reward)

    data = RewardPointResponse.model_validate(reward).model_dump()
    return success(message="Reward successfully updated", data=data)

@router.delete('/{reward_id}')
def delete_reward_point(
        reward_id: int,
        db: Session = Depends(get_db)
):
    reward = db.execute(select(TrashCategory).where(TrashCategory.id == reward_id)).scalar_one_or_none()

    if not reward:
        return error(message="Reward not found")

    db.delete(reward)
    db.commit()
    return info(message="Reward successfully deleted")