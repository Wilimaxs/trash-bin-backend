from sqlalchemy import Integer, String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class DisposalHistory(Base):
    __tablename__ = "disposal_histories"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    trash_bin_id: Mapped[int] = mapped_column(ForeignKey("trash_bins.id"), nullable=False, index=True)
    trash_category_id: Mapped[int] = mapped_column(ForeignKey("trash_categories.id"), nullable=False, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)

    image_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    points_earned: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    user = relationship(argument="User", back_populates="disposal_histories")
    trash_bin = relationship(argument="TrashBin", back_populates="disposal_histories")
    trash_category = relationship(argument="TrashCategory", back_populates="disposal_histories")