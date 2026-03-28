from sqlalchemy import Integer, ForeignKey, Boolean

from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base


class BinSession(Base):
    __tablename__ = "bin_sessions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    trash_bin_id: Mapped[int] = mapped_column(ForeignKey("trash_bins.id"), nullable=False, index=True)

    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    user = relationship(argument="User", back_populates="bin_sessions")
    trash_bin = relationship(argument="TrashBin", back_populates="bin_sessions")
