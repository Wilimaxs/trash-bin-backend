import io
import os
from datetime import timedelta

from PIL import Image
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import get_wib_time
from app.db.deps import get_db
from app.models.bin_session import BinSession
from app.models.disposal_history import DisposalHistory
from app.models.trash_bin import TrashBin
from app.models.trash_category import TrashCategory
from app.models.user import User
from app.schemas.common import success

try:
    from ultralytics import YOLO
except ImportError:
    YOLO = None

router = APIRouter(prefix="/iot", tags=["iot"])

# Set timeout 5 menit
IDLE_TIMEOUT_MINUTES = 5

# Load model secara global agar tidak me-load ulang setiap request masuk
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
MODEL_PATH = os.path.join(BASE_DIR, "ml_model", "version1.pt")

try:
    if YOLO is not None and os.path.exists(MODEL_PATH):
        yolo_model = YOLO(MODEL_PATH)
    else:
        yolo_model = None
except Exception as e:
    yolo_model = None
    print(f"Error loading YOLO model: {e}")

@router.post("/detect")
async def detect_trash(
    qr_code: str = Form(..., description="UUID / QR Code of the trash bin"),
    image: UploadFile = File(..., description="Image captured by ESP32 camera"),
    db: Session = Depends(get_db)
):
    # 1. Cari TrashBin berdasarkan qr_code
    trash_bin = db.execute(select(TrashBin).where(TrashBin.qr_code == qr_code)).scalar_one_or_none()
    if not trash_bin:
        raise HTTPException(status_code=404, detail="Trash bin not found")

    # 2. Cari sesi aktif di tong sampah tersebut
    active_session = db.execute(
        select(BinSession)
        .where(BinSession.trash_bin_id == trash_bin.id)
        .where(BinSession.is_active == True)
    ).scalar_one_or_none()

    current_time = get_wib_time()
    user_id = None

    if active_session:
        # Pengecekan Timeout
        last_activity = active_session.last_activity_at or current_time
        
        # Samakan timezone jika ada perbedaan offset-aware dan offset-naive
        if last_activity.tzinfo is None and current_time.tzinfo is not None:
            last_activity = last_activity.replace(tzinfo=current_time.tzinfo)
        elif last_activity.tzinfo is not None and current_time.tzinfo is None:
            current_time = current_time.replace(tzinfo=last_activity.tzinfo)

        time_diff = current_time - last_activity
        
        if time_diff > timedelta(minutes=IDLE_TIMEOUT_MINUTES):
            # Jika sudah lebih dari 5 menit, putuskan sesi otomatis
            active_session.is_active = False
            db.commit()
            # Sesi sudah diputus, jadi tidak ada user teregister untuk sampah ini
        else:
            # Sesi masih valid, update last_activity_at
            active_session.last_activity_at = current_time
            user_id = active_session.user_id
            db.commit()

    # 4. PROSES INFERENSI YOLOv8
    if yolo_model is None:
        raise HTTPException(status_code=500, detail="Machine learning model is not available")

    confidence = 0.0
    try:
        # Proses gambar menjadi format yang bisa dibaca YOLO (seperti PIL Image)
        image_bytes = await image.read()
        img = Image.open(io.BytesIO(image_bytes))

        # Inferensi dipanggil ke model
        results = yolo_model(img, verbose=False)

        # Cek apakah YOLO mendapatkan minimal 1 objek
        if len(results) > 0 and len(results[0].boxes) > 0:
            # Ambil object dengan confidence paling tinggi (default Ultralytics nge-sort dari tertinggi)
            best_box = results[0].boxes[0]
            class_id = int(best_box.cls[0].item())
            confidence = float(best_box.conf[0].item())
            
            # Ambil string nama kelas (contoh: "plastic_bag") dari class list YOLO
            detected_sub_category = yolo_model.names[class_id]
        else:
            detected_sub_category = None

    except Exception as err:
        print(f"Error during YOLO inference: {err}")
        # Jika inference gagal / error, kita anggap tidak terdeteksi
        detected_sub_category = None
    
    # Cari TrashCategory yang sesuai dengan hasil deteksi YOLO
    if detected_sub_category:
        trash_category = db.execute(
            select(TrashCategory).where(TrashCategory.sub_category == detected_sub_category)
        ).scalar_one_or_none()
    else:
        trash_category = None

    # Jika gak kedeteksi atau kategori tidak ada di DB, default compartment_type ke tipe 'organic' dari DB (bukan hardcode murni)
    if trash_category:
        reward_points = trash_category.reward_points
        compartment_type = trash_category.compartment_type
        trash_category_id = trash_category.id
    else:
        reward_points = 0
        trash_category_id = None
        # Ambil nama compartment_type "organic" langsung dari DB agar dinamis mengikuti data yang ada di DB
        fallback_cat = db.execute(select(TrashCategory).where(TrashCategory.compartment_type == "organic")).scalars().first()
        compartment_type = fallback_cat.compartment_type if fallback_cat else "organic"

    # Jika ada sesi aktif dan belum timeout, berikan point
    if user_id and active_session and active_session.is_active:
        active_session.total_points += reward_points
        if trash_category_id: # Hanya tambah items count jika memang valid terklasifikasi, atau bebas? (Asumsi tambah 1 items tetap)
            pass
        active_session.total_items += 1

        # Tambahkan point juga ke total_points di table users
        user = db.execute(select(User).where(User.id == user_id)).scalar_one_or_none()
        if user:
            user.total_points += reward_points

        db.commit()

    # 5. Catat ke history (user_id bisa null jika tidak ada orang yang connect atau keburu timeout)
    new_history = DisposalHistory(
        user_id=user_id,
        trash_bin_id=trash_bin.id,
        trash_category_id=trash_category_id,
        image_url=None,
        points_earned=reward_points
    )
    db.add(new_history)
    db.commit()
    db.refresh(new_history)

    # 6. Response yang diperlukan oleh ESP32
    # ESP32 cukup butuh mengetahui kompartemen mana yang harus dibuka
    return success(
        message="Trash detected successfully",
        data={
            "compartment_type": compartment_type,
            "session_active": bool(user_id),
            "detected_sub_category": detected_sub_category,
            "confidence": round(confidence, 2)
        }
    )

from pydantic import BaseModel

class UpdateCapacityRequest(BaseModel):
    qr_code: str
    capacity_organic: int
    capacity_inorganic: int
    capacity_b3: int

@router.post("/update-capacity")
def update_capacity(
    request: UpdateCapacityRequest,
    db: Session = Depends(get_db)
):
    trash_bin = db.execute(select(TrashBin).where(TrashBin.qr_code == request.qr_code)).scalar_one_or_none()
    
    if not trash_bin:
        raise HTTPException(status_code=404, detail="Trash bin not found")

    trash_bin.capacity_organic = request.capacity_organic
    trash_bin.capacity_inorganic = request.capacity_inorganic
    trash_bin.capacity_b3 = request.capacity_b3

    db.commit()

    return success(
        message="Capacity updated successfully"
    )
