from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.deps import get_db
from app.models import TrashBin
from app.schemas.admin_device_request import DeviceResponse, DeviceCreateUpdate
from app.schemas.common import success, error, info

router = APIRouter(prefix="/admin/device", tags=["admin"])

@router.get("/")
def get_devices(db: Session = Depends(get_db)):
    db_devices = db.execute(select(TrashBin)).scalars().all()
    data = [DeviceResponse.model_validate(d).model_dump() for d in db_devices]
    return success(message="Success retrieve devices", data=data)

# 2. CREATE
@router.post("/")
def create_device(device: DeviceCreateUpdate, db: Session = Depends(get_db)):
    # Validasi QR unik
    existing_qr = db.execute(select(TrashBin).where(TrashBin.qr_code == device.qr_code)).scalar_one_or_none()
    if existing_qr:
        return error(message="QR Code sudah digunakan")

    # Set kapasitas default 0
    new_device = TrashBin(
        qr_code=device.qr_code,
        location_name=device.location_name,
        capacity_organic=0,
        capacity_inorganic=0,
        capacity_b3=0
    )
    db.add(new_device)
    db.commit()
    db.refresh(new_device)

    data = DeviceResponse.model_validate(new_device).model_dump()
    return success(message="Device successfully created", data=data)

# 3. UPDATE
@router.put("/{device_id}")
def update_device(device_id: int, device: DeviceCreateUpdate, db: Session = Depends(get_db)):
    db_device = db.execute(select(TrashBin).where(TrashBin.id == device_id)).scalar_one_or_none()
    if not db_device:
        return error(message="Device not found")

    # Validasi QR unik jika QR diubah
    if device.qr_code != db_device.qr_code:
        existing_qr = db.execute(select(TrashBin).where(TrashBin.qr_code == device.qr_code)).scalar_one_or_none()
        if existing_qr:
            return error(message="QR Code sudah digunakan oleh device lain")

    # Hanya update field yang diizinkan
    db_device.qr_code = device.qr_code
    db_device.location_name = device.location_name

    db.commit()
    db.refresh(db_device)

    data = DeviceResponse.model_validate(db_device).model_dump()
    return success(message="Device successfully updated", data=data)

# 4. DELETE
@router.delete("/{device_id}")
def delete_device(device_id: int, db: Session = Depends(get_db)):
    db_device = db.execute(select(TrashBin).where(TrashBin.id == device_id)).scalar_one_or_none()
    if not db_device:
        return error(message="Device not found")

    db.delete(db_device)
    db.commit()
    return info(message="Device successfully deleted")