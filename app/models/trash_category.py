from sqlalchemy import String, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class TrashCategory(Base):
    __tablename__ = "trash_categories"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    compartment_type: Mapped[str] = mapped_column(String(50), nullable=False)  # organic/inorganic/b3
    sub_category: Mapped[str | None] = mapped_column(String(255), nullable=True)
    reward_points: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    disposal_histories = relationship(argument="DisposalHistory", back_populates="trash_category", cascade="all, delete-orphan")
