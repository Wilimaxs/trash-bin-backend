import asyncio
import json
from datetime import timedelta

from fastapi import APIRouter, Depends, Request
from fastapi.responses import StreamingResponse
from sqlalchemy import select

from app.core.config import get_wib_time
from app.db.session import SessionLocal
from app.models.bin_session import BinSession
from app.models.disposal_history import DisposalHistory
from app.models.trash_bin import TrashBin
from app.models.trash_category import TrashCategory
from app.models.user import User
from app.services.api_header import get_current_user

router = APIRouter(prefix="/stream", tags=["stream"])

async def dashboard_event_generator(request: Request, user_id: int):
    """
    Generator untuk SSE yang mengirimkan balasan data real-time dashboard dengan durasi/jeda 2 detik.
    Akan berhenti (break) ketika client (mobile app) disconnect.
    """
    while True:
        # Pengecekan jika client terputus (untuk mencegah SSE jalan terus-terusan tanpa client)
        if await request.is_disconnected():
            break

        db = SessionLocal()
        try:
            # 1. Cek Curent Active Session user
            active_session = db.execute(
                select(BinSession)
                .where(BinSession.user_id == user_id)
                .where(BinSession.is_active == True)
            ).scalar_one_or_none()
            
            # Cek Idle Timeout 5 menit
            if active_session:
                current_time = get_wib_time()
                last_activity = active_session.last_activity_at or current_time
                
                if last_activity.tzinfo is None and current_time.tzinfo is not None:
                    last_activity = last_activity.replace(tzinfo=current_time.tzinfo)
                elif last_activity.tzinfo is not None and current_time.tzinfo is None:
                    current_time = current_time.replace(tzinfo=last_activity.tzinfo)
                
                if current_time - last_activity > timedelta(minutes=5):
                    # Timeout tercapai
                    active_session.is_active = False
                    db.commit()
                    active_session = None

            if not active_session:
                # User tidak punya sesi aktif (Locked state) atau sudah timeout
                payload = {
                    "is_connected": False,
                    "message": "Please scan QR to connect."
                }
                yield f"data: {json.dumps(payload)}\n\n"
                break
            else:
                # 2. Dapatkan data kapasitas dari TrashBin terkait
                trash_bin = db.execute(
                    select(TrashBin).where(TrashBin.id == active_session.trash_bin_id)
                ).scalar_one_or_none()
                
                # 3. Dapatkan aktivitas buang sampah selama sesi ini untuk live activity
                session_start_time = active_session.created_at
                disposals = db.execute(
                    select(DisposalHistory)
                    .where(DisposalHistory.user_id == user_id)
                    .where(DisposalHistory.trash_bin_id == trash_bin.id)
                    .where(DisposalHistory.created_at >= session_start_time)
                    .order_by(DisposalHistory.created_at.desc())
                    .limit(10)
                ).scalars().all()
                
                recent_activity = []
                for disposal in disposals:
                    category_name = None
                    if disposal.trash_category_id:
                        cat = db.execute(
                            select(TrashCategory).where(TrashCategory.id == disposal.trash_category_id)
                        ).scalar_one_or_none()
                        if cat:
                            category_name = cat.sub_category
                    
                    recent_activity.append({
                        "category": category_name,
                        "points_earned": disposal.points_earned,
                        "time": disposal.created_at.isoformat() if disposal.created_at else None
                    })
                
                payload = {
                    "is_connected": True,
                    "bin_name": trash_bin.location_name if trash_bin else "Unknown Bin",
                    "total_points": active_session.total_points,
                    "total_items": active_session.total_items,
                    "capacity_organic": trash_bin.capacity_organic if trash_bin else 0,
                    "capacity_inorganic": trash_bin.capacity_inorganic if trash_bin else 0,
                    "capacity_b3": trash_bin.capacity_b3 if trash_bin else 0,
                    "live_activity": recent_activity
                }
            
            # Format Server-Sent Events (SSE): prefix 'data: ' dan diakhiri '\n\n'
            yield f"data: {json.dumps(payload)}\n\n"

        except Exception as e:
            # Jika ada error database atau lainnya, kirim SSE error format
            error_payload = {"error": str(e)}
            yield f"data: {json.dumps(error_payload)}\n\n"
        
        finally:
            db.close()
            
        await asyncio.sleep(2)  # jeda/interval pengiriman real-time per 2 detik per client

@router.get("/dashboard")
async def stream_dashboard(
    request: Request,
    current_user: User = Depends(get_current_user)
):
    """
    Endpoint SSE (Server-Sent Events) untuk Mobile App memantau real-time dashboard.
    Tidak memerlukan respons konvensional, client me-listen selamanya secara unidirectional.
    """
    return StreamingResponse(
        dashboard_event_generator(request, current_user.id), 
        media_type="text/event-stream"
    )
