from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class TrashBin(Base):
    __tablename__ = "trash_bins"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    qr_code: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)

    location_name: Mapped[str | None] = mapped_column(String(255), nullable=True)

    capacity_organic: Mapped[int | None] = mapped_column(Integer, nullable=True)
    capacity_inorganic: Mapped[int | None] = mapped_column(Integer, nullable=True)
    capacity_b3: Mapped[int | None] = mapped_column(Integer, nullable=True)

    bin_sessions = relationship(argument="BinSession", back_populates="trash_bin", cascade="all, delete-orphan")
    disposal_histories = relationship(argument="DisposalHistory", back_populates="trash_bin", cascade="all, delete-orphan")
