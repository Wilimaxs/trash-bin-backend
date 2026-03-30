from pydantic import BaseModel, Field, EmailStr

class ForgotPasswordRequest(BaseModel):
    """
    Schema validation for forgot password request.
    """
    email: EmailStr = Field(..., max_length=255, description="Registered email")

