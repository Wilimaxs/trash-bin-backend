from pydantic import BaseModel, Field

class RefreshTokenRequest(BaseModel):
    refresh_token: str = Field(..., description="The valid refresh token string")

