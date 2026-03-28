import os
from dotenv import load_dotenv

load_dotenv()

# Default: SQLite database
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./trash_bin.db")

# JWT secret key
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "default-secret-key")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1440"))
OTP_TOKEN_EXPIRE_MINUTES = int(os.getenv("OTP_TOKEN_EXPIRE_MINUTES", "5"))

# Resend API Key
RESEND_API_KEY = os.getenv("RESEND_API_KEY", "")
