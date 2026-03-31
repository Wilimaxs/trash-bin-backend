from fastapi import APIRouter, Depends, Form, UploadFile, File, HTTPException
from sqlalchemy import func, select
from sqlalchemy.orm import Session
import os
import shutil
import uuid

from app.db.deps import get_db
from app.models.disposal_history import DisposalHistory
from app.models.user import User
from app.schemas.common import success
from app.services.api_header import get_current_user

router = APIRouter(prefix="/user", tags=["user"])


@router.get("/profile")
def get_user_profile(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Counting total items in DisposalHistory for the current user
    count_query = select(func.count()).select_from(DisposalHistory).where(DisposalHistory.user_id == current_user.id)
    total_items = db.scalar(count_query) or 0

    # Take the year from the created_at date if available, otherwise default to 2024
    member_since_year = current_user.created_at.strftime("%Y") if current_user.created_at else "2024"

    return success(
        message="Success retrieve user profile",
        data={
            "full_name": current_user.full_name,
            "email": current_user.email,
            "avatar_url": current_user.avatar_url,
            "member_since": f"Member since {member_since_year}",
            "total_points": current_user.total_points,
            "total_items": total_items
        }
    )


@router.post("/profile")
def update_user_profile(
    full_name: str | None = Form(None),
    avatar: UploadFile | None = File(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if full_name is not None:
        current_user.full_name = full_name

    if avatar is not None:
        # Validate that it's actually an image
        allowed_types = ["image/jpeg", "image/png", "image/jpg"]
        if avatar.content_type not in allowed_types:
            raise HTTPException(status_code=400, detail="Only JPEG, JPG, and PNG files are allowed")
            
        # Create a unique filename
        filename = avatar.filename if avatar.filename else "image.jpg"
        file_ext = os.path.splitext(filename)[1]
        
        if not file_ext:
            ext_map = {"image/jpeg": ".jpg", "image/jpg": ".jpg", "image/png": ".png"}
            file_ext = ext_map.get(avatar.content_type, ".jpg")
            
        unique_filename = f"avatar_user_{current_user.id}_{uuid.uuid4().hex[:8]}{file_ext}"
        
        # Determine paths
        folder_path = os.path.join("public", "avatars")
        file_path = os.path.join(folder_path, unique_filename)
        
        # Save a file to the local public / avatars folder
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(avatar.file, buffer) # type: ignore
            
        # Delete the old avatar if it exists (Optional cleanup)
        if current_user.avatar_url and current_user.avatar_url.startswith("/public/avatars/"):
            old_file_path = current_user.avatar_url.lstrip("/")
            if os.path.exists(old_file_path):
                try:
                    os.remove(old_file_path)
                except OSError:
                    pass
        
        # Save relative URL to database
        current_user.avatar_url = f"/public/avatars/{unique_filename}"

    db.commit()
    db.refresh(current_user)

    return success(
        message="Profile updated successfully",
        data={
            "id": current_user.id,
            "full_name": current_user.full_name,
            "email": current_user.email,
            "avatar_url": current_user.avatar_url
        }
    )
