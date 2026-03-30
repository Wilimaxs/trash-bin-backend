from pydantic import BaseModel, Field, field_validator, model_validator

class ResetPasswordRequest(BaseModel):
    """
    Schema validation for reset password request.
    """
    reset_token: str = Field(..., description="Token received from verifying the OTP")
    new_password: str = Field(..., min_length=8, max_length=72, description="New Password")
    password_confirmation: str = Field(..., min_length=8, max_length=72, description="Confirm New Password")

    """
    Validation password length and byte limit
    """
    @field_validator("new_password", "password_confirmation")
    @classmethod
    def validate_bcrypt_byte_limit(cls, value: str) -> str:
        if len(value.encode("utf-8")) > 72:
            raise ValueError("Password too long (maximum 72 bytes)")
        return value

    """
    Validation password confirmation 
    """
    @model_validator(mode="after")
    def validate_passwords_match(self) -> 'ResetPasswordRequest':
        if self.new_password != self.password_confirmation:
            raise ValueError("Passwords do not match")
        return self

