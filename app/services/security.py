import bcrypt
import jwt
from datetime import datetime, timedelta, timezone
from app.core.config import JWT_SECRET_KEY, JWT_ALGORITHM


def hash_password(password: str) -> str:
    encoded = password.encode("utf-8")
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(encoded, salt).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    encoded = plain_password.encode("utf-8")
    return bcrypt.checkpw(encoded, hashed_password.encode("utf-8"))


def create_otp_token(email: str, otp_code: str, expires_delta: timedelta) -> str:
    """
    Create a JWT token for OTP verification containing email and OTP code.
    """
    expire = datetime.now(timezone.utc) + expires_delta
    to_encode = {
        "exp": expire,
        "type": "registration",
        "email": email,
        "otp_code": otp_code,
    }
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    return encoded_jwt
