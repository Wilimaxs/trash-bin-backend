import math
import os
import zipfile

from fastapi import APIRouter, Depends, Query, BackgroundTasks
from fastapi.responses import FileResponse
from sqlalchemy import select, func, desc
from sqlalchemy.orm import Session

from app.db.deps import get_db
from app.models import DisposalHistory
from app.schemas.common import success, error

router = APIRouter(prefix="/admin/unknown-disposal", tags=["admin"])

def delete_file_safe(path: str):
    if path and os.path.exists(path):
        try:
            os.remove(path)
        except Exception:
            pass

@router.get("/")
def get_unknown_disposals(
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db)
):
    offset = (page - 1) * size

    query = select(DisposalHistory).where(DisposalHistory.trash_category_id == None)
    
    total = db.scalar(select(func.count()).select_from(query.subquery())) or 0
    total_pages = math.ceil(total / size) if total > 0 else 0
    
    records = db.execute(
        query.order_by(desc(DisposalHistory.created_at)).offset(offset).limit(size)
    ).scalars().all()
    
    data = []
    for r in records:
        data.append({
            "id": r.id,
            "trash_bin_id": r.trash_bin_id,
            "bin_location": r.trash_bin.location_name if r.trash_bin else "Unknown",
            "image_url": r.image_url,
            "created_at": r.created_at.strftime("%Y-%m-%d %H:%M:%S") if r.created_at else None
        })
        
    return success("Berhasil mengambil data sampah tidak dikenali", data={
        "total": total,
        "page": page,
        "size": size,
        "total_pages": total_pages,
        "items": data
    })

@router.delete("/all")
def delete_all_unknown_disposals(db: Session = Depends(get_db)):
    records = db.execute(select(DisposalHistory).where(DisposalHistory.trash_category_id == None)).scalars().all()
    for r in records:
        if r.image_url:
            path = r.image_url.lstrip("/")
            delete_file_safe(path)
        db.delete(r)
    db.commit()
    return success("Semua data berhasil dihapus")

@router.delete("/{id}")
def delete_unknown_disposal(id: int, db: Session = Depends(get_db)):
    r = db.get(DisposalHistory, id)
    if not r or r.trash_category_id is not None:
        return error("Data tidak ditemukan atau sudah memiliki kategori")
    
    if r.image_url:
        path = r.image_url.lstrip("/")
        delete_file_safe(path)
        
    db.delete(r)
    db.commit()
    return success("Data berhasil dihapus")

@router.get("/download-all")
def download_all_unknown(background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    records = db.execute(select(DisposalHistory).where(DisposalHistory.trash_category_id == None)).scalars().all()
    if not records:
        return error("Tidak ada data untuk di-download")
        
    zip_path = "temp_unknown_disposals.zip"
    with zipfile.ZipFile(zip_path, 'w') as zipf:
        for r in records:
            path = r.image_url.lstrip("/") if r.image_url else ""
            if path and os.path.exists(path):
                ext = os.path.splitext(path)[1]
                zipf.write(path, arcname=f"unknown_{r.id}{ext}")
                
    for r in records:
        db.delete(r)
    db.commit()
    
    def cleanup():
        for r in records:
            path = r.image_url.lstrip("/") if r.image_url else ""
            delete_file_safe(path)
        delete_file_safe(zip_path)
        
    background_tasks.add_task(cleanup)
    return FileResponse(zip_path, filename="unknown_disposals.zip")

@router.get("/download/{id}")
def download_unknown_disposal(id: int, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    r = db.get(DisposalHistory, id)
    if not r or r.trash_category_id is not None:
        return error("Data tidak ditemukan")
        
    path = r.image_url.lstrip("/") if r.image_url else ""
    if not path or not os.path.exists(path):
        return error("File gambar tidak ditemukan")
        
    db.delete(r)
    db.commit()
    
    background_tasks.add_task(delete_file_safe, path)
    return FileResponse(path, filename=f"unknown_{id}{os.path.splitext(path)[1]}")
