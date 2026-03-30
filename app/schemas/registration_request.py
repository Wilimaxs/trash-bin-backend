from typing import Optional

from pydantic import BaseModel, Field, field_validator, model_validator, EmailStr


class RegistrationRequest(BaseModel):
    """
    Schema validation registration request.
    """
    email: EmailStr = Field(..., max_length=255, description="Email")
    password: str = Field(..., min_length=8, max_length=72, description="Password")
    password_confirmation: str = Field(..., min_length=8, max_length=72, description="Password Confirmation")
    full_name: Optional[str] = Field(default=None, max_length=255, description="Full Name")

    """
    Normalize email address
    """
    @field_validator("email", mode="before")
    @classmethod
    def normalize_email(cls, value: str) -> str:
        if isinstance(value, str):
            return value.strip().lower()
        return value

    """
    Validation password length and byte limit
    """
    @field_validator("password", "password_confirmation")
    @classmethod
    def validate_bcrypt_byte_limit(cls, value: str) -> str:
        if len(value.encode("utf-8")) > 72:
            raise ValueError("Password too long (maximum 72 bytes)")
        return value

    """
    Validation password confirmation 
    """
    @model_validator(mode="after")
    def validate_passwords_match(self) -> 'RegistrationRequest':
        if self.password != self.password_confirmation:
            raise ValueError("Passwords do not match")
        return self
