from typing import Optional

from pydantic import BaseModel


class DeviceCreateUpdate(BaseModel):
    qr_code: str
    location_name: Optional[str] = None

class DeviceResponse(BaseModel):
    id: int
    qr_code: str
    location_name: Optional[str] = None
    capacity_organic: int = 0
    capacity_inorganic: int = 0
    capacity_b3: int = 0

    class Config:
        from_attributes = True