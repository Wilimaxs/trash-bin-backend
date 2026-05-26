import io
import os
import uuid
from typing import Optional

# cv2 dan np didefinisikan di kedua blok (try & except) agar tidak ada warning linter
try:
    import cv2
    import numpy as np
    CV2_AVAILABLE = True
except ImportError:
    cv2 = None  # type: ignore
    np = None   # type: ignore
    CV2_AVAILABLE = False
    print("WARNING: opencv-python-headless tidak terinstall. Install dengan: pip install opencv-python-headless")

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

# ============================================================
# KONFIGURASI UMUM
# ============================================================
IDLE_TIMEOUT_MINUTES = 5

BASE_DIR = os.getcwd()
MODEL_PATH = os.path.join(BASE_DIR, "ml_model", "version1.pt")
UPLOAD_DIR = os.path.join(BASE_DIR, "public", "disposals")
os.makedirs(UPLOAD_DIR, exist_ok=True)

# ============================================================
# KONFIGURASI BACKGROUND SUBTRACTION
# ============================================================

# Mode debug: True = print log detail di terminal, False = silent (production)
BG_DEBUG = True

# Minimum area foreground (pixel) agar dianggap ada objek.
# Tuning: jalankan endpoint /iot/bg-debug dulu untuk cari nilai yang pas.
# Gunakan /bg-debug → masukkan sampah terkecil → lihat max_area → set nilai di bawahnya
BG_MIN_AREA = 300

# Jumlah frame pertama untuk warmup MOG2 belajar background.
# Warmup hanya terjadi saat SERVER restart, bukan saat ESP restart.
# Selama warmup: /detect-v2 return idle, ESP diam, tong harus kosong.
BG_WARMUP_FRAMES = 30

# Sensitivitas perubahan pixel.
# 30-40 = sensitif, 50-70 = balanced, >80 = butuh perubahan besar
BG_VAR_THRESHOLD = 50

# ============================================================
# BACKGROUND SUBTRACTOR - Per trash bin (key = qr_code)
# Disimpan di memory server. ESP restart tidak mereset ini.
# ============================================================
_bg_subtractors: dict = {}


def _get_bg_subtractor(qr_code: str) -> dict:
    """
    Ambil atau buat background subtractor untuk trash bin tertentu.
    Setiap trash bin punya subtractor sendiri karena background bisa beda.
    """
    if qr_code not in _bg_subtractors:
        _bg_subtractors[qr_code] = {
            "subtractor": cv2.createBackgroundSubtractorMOG2(
                history=500,
                varThreshold=BG_VAR_THRESHOLD,
                detectShadows=False
            ),
            "frame_count": 0
        }
        if BG_DEBUG:
            print(f"[BG SUBTRACTION] Subtractor baru dibuat untuk bin: {qr_code}")
    return _bg_subtractors[qr_code]


def check_foreground(image_bytes: bytes, qr_code: str, bypass_warmup: bool = False) -> dict:
    """
    Cek apakah ada objek (foreground) di frame yang masuk.

    Parameters:
    - image_bytes   : raw bytes gambar dari ESP
    - qr_code       : identifikasi trash bin
    - bypass_warmup : True = skip cek warmup, langsung return hasil MOG2 (khusus /bg-debug)

    Returns dict:
    - ada_objek (bool)     : True jika ada objek signifikan
    - is_warmup (bool)     : True jika masih warmup (hanya relevan saat bypass_warmup=False)
    - max_area (int)       : area pixel contour terbesar
    - fg_pixel_count (int) : total pixel foreground
    - fg_ratio (float)     : rasio foreground vs total pixel
    """
    bg_data = _get_bg_subtractor(qr_code)
    subtractor = bg_data["subtractor"]

    # Decode image bytes ke numpy array
    nparr = np.frombuffer(image_bytes, np.uint8)
    frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    # Fallback jika gambar tidak bisa di-decode
    if frame is None:
        if BG_DEBUG:
            print(f"[BG SUBTRACTION] WARNING: Gambar tidak bisa di-decode untuk bin {qr_code}")
        return {
            "ada_objek": True,
            "is_warmup": False,
            "max_area": 0,
            "fg_pixel_count": 0,
            "fg_ratio": 0.0
        }

    # Resize untuk efisiensi
    frame_resized = cv2.resize(frame, (320, 240))

    # Apply ke MOG2 — selalu dijalankan agar MOG2 terus belajar
    fg_mask = subtractor.apply(frame_resized)
    bg_data["frame_count"] += 1
    frame_count = bg_data["frame_count"]

    # Bersihkan noise kecil
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
    fg_mask_clean = cv2.morphologyEx(fg_mask, cv2.MORPH_OPEN, kernel)

    # Cek warmup — di-skip jika dipanggil dari /bg-debug (bypass_warmup=True)
    if not bypass_warmup and frame_count <= BG_WARMUP_FRAMES:
        if BG_DEBUG:
            print(f"[BG SUBTRACTION] {qr_code} - WARMUP {frame_count}/{BG_WARMUP_FRAMES} - ESP idle")
        return {
            "ada_objek": False,
            "is_warmup": True,
            "max_area": 0,
            "fg_pixel_count": 0,
            "fg_ratio": 0.0
        }

    # Hitung foreground
    fg_pixel_count = cv2.countNonZero(fg_mask_clean)
    total_pixels = fg_mask_clean.shape[0] * fg_mask_clean.shape[1]
    fg_ratio = fg_pixel_count / total_pixels

    # Cari contours
    contours, _ = cv2.findContours(fg_mask_clean, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    max_area = 0
    ada_objek = False
    for contour in contours:
        area = cv2.contourArea(contour)
        if area > max_area:
            max_area = area
        if area >= BG_MIN_AREA:
            ada_objek = True

    if BG_DEBUG:
        warmup_note = f" [WARMUP {frame_count}/{BG_WARMUP_FRAMES} - bypass]" if bypass_warmup and frame_count <= BG_WARMUP_FRAMES else ""
        status = "ADA OBJEK ✓" if ada_objek else "BACKGROUND (idle)"
        print(f"[BG SUBTRACTION] {qr_code} | Frame #{frame_count}{warmup_note} | {status}")
        print(f"[BG SUBTRACTION] → FG pixels: {fg_pixel_count} | Ratio: {fg_ratio:.3f} | Max area: {max_area}px | Threshold: {BG_MIN_AREA}px")

    return {
        "ada_objek": ada_objek,
        "is_warmup": bypass_warmup and frame_count <= BG_WARMUP_FRAMES,
        "max_area": int(max_area),
        "fg_pixel_count": fg_pixel_count,
        "fg_ratio": round(fg_ratio, 4)
    }


# ============================================================
# DEBUG MODEL YOLO
# ============================================================
print("====== DEBUG MODEL YOLO ======")
print(f"Mencari model di folder: {MODEL_PATH}")
print(f"Apakah filenya beneran ada?: {os.path.exists(MODEL_PATH)}")
print("==============================")

try:
    if YOLO is not None and os.path.exists(MODEL_PATH):
        yolo_model = YOLO(MODEL_PATH)
    else:
        yolo_model = None
except Exception as e:
    yolo_model = None
    print(f"Error loading YOLO model: {e}")


# ============================================================
# ENDPOINT: /detect-v2 — dengan Background Subtraction
# Ganti URL ESP dari /iot/detect ke /iot/detect-v2
# Rollback: ganti balik ke /iot/detect di kodingan ESP
# ============================================================
@router.post("/detect-v2")
def detect_trash_v2(
        qr_code: str = Form(..., description="UUID / QR Code of the trash bin"),
        image: UploadFile = File(..., description="Image captured by ESP32 camera"),
        capacity_organic: Optional[int] = Form(None, description="Current capacity of organic bin"),
        capacity_inorganic: Optional[int] = Form(None, description="Current capacity of inorganic bin"),
        capacity_b3: Optional[int] = Form(None, description="Current capacity of b3 bin"),
        db: Session = Depends(get_db)
):
    # ── 1. Cek opencv tersedia ────────────────────────────────────────────────
    if not CV2_AVAILABLE:
        raise HTTPException(
            status_code=503,
            detail="opencv tidak terinstall. Jalankan: pip install opencv-python-headless"
        )

    # ── 2. Cari TrashBin ──────────────────────────────────────────────────────
    trash_bin = db.execute(select(TrashBin).where(TrashBin.qr_code == qr_code)).scalar_one_or_none()
    if not trash_bin:
        raise HTTPException(status_code=404, detail="Trash bin not found")

    if capacity_organic is not None:
        trash_bin.capacity_organic = capacity_organic
    if capacity_inorganic is not None:
        trash_bin.capacity_inorganic = capacity_inorganic
    if capacity_b3 is not None:
        trash_bin.capacity_b3 = capacity_b3

    # ── 3. Baca image bytes SEKALI ────────────────────────────────────────────
    image_bytes = image.file.read()

    # ── 4. Background Subtraction ─────────────────────────────────────────────
    # bypass_warmup=False → warmup dihormati, ESP idle saat warmup
    bg_result = check_foreground(image_bytes, qr_code, bypass_warmup=False)

    if not bg_result["ada_objek"]:
        # Background murni atau masih warmup → ESP idle, skip YOLO & history
        if BG_DEBUG:
            warmup_info = " (WARMUP)" if bg_result["is_warmup"] else ""
            print(f"[DETECT-V2] {qr_code} → IDLE{warmup_info}")
        return success(
            message="No object detected, background only",
            data={
                "compartment_type": "idle",
                "is_warmup": bg_result["is_warmup"],
                "session_active": False,
                "detected_sub_category": None,
                "confidence": 0.0,
                "bg_debug": bg_result if BG_DEBUG else None
            }
        )

    # ── 5. Cek sesi aktif ─────────────────────────────────────────────────────
    active_session = db.execute(
        select(BinSession)
        .where(BinSession.trash_bin_id == trash_bin.id)
        .where(BinSession.is_active == True)
    ).scalar_one_or_none()

    current_time = get_wib_time()
    user_id = None

    if active_session:
        from app.utils.time import is_idle_timeout
        last_activity = active_session.last_activity_at or current_time

        if is_idle_timeout(last_activity, current_time, IDLE_TIMEOUT_MINUTES):
            active_session.is_active = False
            db.commit()
        else:
            active_session.last_activity_at = current_time
            user_id = active_session.user_id
            db.commit()

    # ── 6. Inferensi YOLO ─────────────────────────────────────────────────────
    if yolo_model is None:
        raise HTTPException(status_code=500, detail="Machine learning model is not available")

    confidence = 0.0
    saved_image_url = None
    detected_sub_category = None

    try:
        ext = image.filename.split('.')[-1] if image.filename and '.' in image.filename else 'jpg'
        filename = f"{uuid.uuid4().hex}.{ext}"
        filepath = os.path.join(UPLOAD_DIR, filename)
        with open(filepath, "wb") as f:
            f.write(image_bytes)
        saved_image_url = f"/public/disposals/{filename}"

        img = Image.open(io.BytesIO(image_bytes))
        results = yolo_model(img, verbose=False)

        if len(results) > 0 and len(results[0].boxes) > 0:
            best_box = results[0].boxes[0]
            class_id = int(best_box.cls[0].item())
            confidence = float(best_box.conf[0].item())
            detected_sub_category = yolo_model.names[class_id]

            if BG_DEBUG:
                print(f"[YOLO] Deteksi: {detected_sub_category} (conf: {confidence:.2f})")
        else:
            if BG_DEBUG:
                print(f"[YOLO] Tidak ada deteksi → safety net organic")

    except Exception as err:
        print(f"[YOLO] Error inference: {err}")
        detected_sub_category = None

    # ── 7. Tentukan compartment_type ──────────────────────────────────────────
    if detected_sub_category:
        trash_category = db.execute(
            select(TrashCategory).where(TrashCategory.sub_category == detected_sub_category)
        ).scalar_one_or_none()
    else:
        trash_category = None

    if trash_category:
        reward_points = trash_category.reward_points
        compartment_type = trash_category.compartment_type
        trash_category_id = trash_category.id
    else:
        # Safety net: BG confirm ada objek, tapi YOLO gagal → organic
        reward_points = 0
        trash_category_id = None
        fallback_cat = db.execute(
            select(TrashCategory).where(TrashCategory.compartment_type == "organic")
        ).scalars().first()
        compartment_type = fallback_cat.compartment_type if fallback_cat else "organic"

        if BG_DEBUG:
            print(f"[DETECT-V2] Safety net aktif → compartment: {compartment_type}")

    # ── 8. Update poin sesi ───────────────────────────────────────────────────
    if user_id and active_session and active_session.is_active:
        active_session.total_points += reward_points
        active_session.total_items += 1

        user = db.execute(select(User).where(User.id == user_id)).scalar_one_or_none()
        if user:
            user.total_points += reward_points

        db.commit()

    # ── 9. Simpan ke history ──────────────────────────────────────────────────
    new_history = DisposalHistory(
        user_id=user_id,
        trash_bin_id=trash_bin.id,
        trash_category_id=trash_category_id,
        image_url=saved_image_url,
        points_earned=reward_points
    )
    db.add(new_history)
    db.commit()
    db.refresh(new_history)

    # ── 10. Response ke ESP32 ─────────────────────────────────────────────────
    return success(
        message="Trash detected successfully",
        data={
            "compartment_type": compartment_type,
            "is_warmup": False,
            "session_active": bool(user_id),
            "detected_sub_category": detected_sub_category,
            "confidence": round(confidence, 2),
            "bg_debug": bg_result if BG_DEBUG else None
        }
    )


# ============================================================
# ENDPOINT: /bg-debug — khusus tuning, tidak kena warmup
# Cara pakai:
#   1. Kirim 30+ frame background kosong (MOG2 belajar background)
#   2. Kirim frame dengan sampah terkecil → catat max_area
#   3. Set BG_MIN_AREA sedikit di bawah nilai max_area sampah terkecil
#   4. Kirim frame background lagi → pastikan max_area < BG_MIN_AREA
# ============================================================
@router.post("/bg-debug")
def bg_debug(
        qr_code: str = Form(..., description="UUID / QR Code of the trash bin"),
        image: UploadFile = File(..., description="Image captured by ESP32 camera"),
):
    # ── 1. Cek opencv tersedia ────────────────────────────────────────────────
    if not CV2_AVAILABLE:
        raise HTTPException(
            status_code=503,
            detail="opencv tidak terinstall. Jalankan: pip install opencv-python-headless"
        )

    image_bytes = image.file.read()

    # bypass_warmup=True → /bg-debug selalu return data nyata, tidak pernah return warmup block
    bg_result = check_foreground(image_bytes, qr_code, bypass_warmup=True)

    return {
        "qr_code": qr_code,
        "bg_result": bg_result,
        "config": {
            "BG_MIN_AREA": BG_MIN_AREA,
            "BG_WARMUP_FRAMES": BG_WARMUP_FRAMES,
            "BG_VAR_THRESHOLD": BG_VAR_THRESHOLD,
        },
        "interpretation": (
            "ADA OBJEK → kalau ini background, naikkan BG_MIN_AREA"
            if bg_result["ada_objek"]
            else "BACKGROUND → kalau ini sampah, turunkan BG_MIN_AREA"
        )
    }


# from pydantic import BaseModel
#
# class UpdateCapacityRequest(BaseModel):
#     qr_code: str
#     capacity_organic: int
#     capacity_inorganic: int
#     capacity_b3: int
#
# @router.post("/update-capacity")
# def update_capacity(
#     request: UpdateCapacityRequest,
#     db: Session = Depends(get_db)
# ):
#     trash_bin = db.execute(select(TrashBin).where(TrashBin.qr_code == request.qr_code)).scalar_one_or_none()
#
#     if not trash_bin:
#         raise HTTPException(status_code=404, detail="Trash bin not found")
#
#     trash_bin.capacity_organic = request.capacity_organic
#     trash_bin.capacity_inorganic = request.capacity_inorganic
#     trash_bin.capacity_b3 = request.capacity_b3
#
#     db.commit()
#
#     return success(
#         message="Capacity updated successfully"
#     )