from pydantic import BaseModel, Field

class VerifyOTPRequest(BaseModel):
    access_token: str = Field(..., description="Access token received from registration")
    otp_code: str = Field(..., description="OTP code sent via email")

