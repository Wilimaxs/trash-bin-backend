from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import select, update

from app.db.deps import get_db
from app.models.bin_session import BinSession
from app.models.trash_bin import TrashBin
from app.models.user import User
from app.schemas.bin_session_request import BinSessionRequest
from app.schemas.common import success
from app.services.api_header import get_current_user

router = APIRouter(prefix="/sessions", tags=["sessions"])


@router.post("/connect")
def connect_session(
    request: BinSessionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Cek apakah tempat sampah terdaftar
    trash_bin = db.execute(select(TrashBin).where(TrashBin.qr_code == request.qr_code)).scalar_one_or_none()
    if not trash_bin:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Trash bin not found"
        )
    trash_bin_id = trash_bin.id

    # Matikan semua sesi aktif di tempat sampah ini (jika ada user sebelumnya yang lupa disconnect)
    # Ini fungsi override (User B menggantikan User A)
    db.execute(
        update(BinSession)
        .where(BinSession.trash_bin_id == trash_bin_id)
        .where(BinSession.is_active == True)
        .values(is_active=False)
    )
    
    # Matikan juga sesi aktif dari current_user jika mungkin dia pindah ke tempat sampah lain tanpa disconnect
    db.execute(
        update(BinSession)
        .where(BinSession.user_id == current_user.id)
        .where(BinSession.is_active == True)
        .values(is_active=False)
    )

    # Buat sesi koneksi baru
    new_session = BinSession(
        user_id=current_user.id,
        trash_bin_id=trash_bin_id,
        is_active=True,
        total_points=0,
        total_items=0
    )
    db.add(new_session)
    db.commit()
    db.refresh(new_session)

    return success(
        message="Successfully connected to trash bin",
        data={
            "session_id": new_session.id,
            "trash_bin_id": new_session.trash_bin_id,
            "qr_code": trash_bin.qr_code,
            "total_points": new_session.total_points,
            "total_items": new_session.total_items
        }
    )


@router.post("/disconnect")
def disconnect_session(
    request: BinSessionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Cek apakah tempat sampah valid berdasarkan qr_code
    trash_bin = db.execute(select(TrashBin).where(TrashBin.qr_code == request.qr_code)).scalar_one_or_none()
    if not trash_bin:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Trash bin not found"
        )
    trash_bin_id = trash_bin.id
    
    # Cek apakah user sedang connect ke tong sampah tsb
    active_session = db.execute(
        select(BinSession)
        .where(BinSession.user_id == current_user.id)
        .where(BinSession.trash_bin_id == trash_bin_id)
        .where(BinSession.is_active == True)
    ).scalar_one_or_none()

    if not active_session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Active session not found for this trash bin"
        )

    active_session.is_active = False
    db.commit()

    return success(message="Successfully disconnected from trash bin", data=None)
