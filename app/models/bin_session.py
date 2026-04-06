from sqlalchemy import Integer, ForeignKey, Boolean, DateTime
from datetime import datetime

from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base
from app.core.config import get_wib_time


class BinSession(Base):
    __tablename__ = "bin_sessions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    trash_bin_id: Mapped[int] = mapped_column(ForeignKey("trash_bins.id"), nullable=False, index=True)

    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    total_points: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    total_items: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    last_activity_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=get_wib_time)

    user = relationship(argument="User", back_populates="bin_sessions")
    trash_bin = relationship(argument="TrashBin", back_populates="bin_sessions")
