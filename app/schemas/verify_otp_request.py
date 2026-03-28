from pydantic import BaseModel, Field, field_validator


class VerifyOTPRequest(BaseModel):
    access_token: str = Field(..., min_length=1, description="Access token received from registration")
    otp_code: str = Field(..., min_length=6, max_length=6, description="6-digit OTP code sent via email")

    @field_validator("otp_code")
    @classmethod
    def validate_otp_digits(cls, value: str) -> str:
        if not value.isdigit():
            raise ValueError("OTP code must contain only numbers")
        return value
