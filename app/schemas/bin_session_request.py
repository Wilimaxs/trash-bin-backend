from pydantic import BaseModel, ConfigDict
from pydantic import Field

class BinSessionRequest(BaseModel):
    qr_code: str = Field(..., description="UUID / QR Code of the trash bin")
    
    model_config = ConfigDict(from_attributes=True)
