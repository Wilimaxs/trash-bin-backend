from typing import Optional
from pydantic import BaseModel, EmailStr

class UpdateProfileRequest(BaseModel):
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None
    avatar_url: Optional[str] = None

