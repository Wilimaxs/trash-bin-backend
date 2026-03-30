from pydantic import BaseModel, Field, EmailStr

class LoginRequest(BaseModel):
    email: EmailStr = Field(..., max_length=255, description="Registered email")
    password: str = Field(..., description="Password")
