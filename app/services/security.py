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


def create_otp_token(email: str, otp_code: str, expires_delta: timedelta, token_type: str = "registration") -> str:
    """
    Create a JWT token for OTP verification containing email, OTP code, and token type.
    """
    expire = datetime.now(timezone.utc) + expires_delta
    to_encode = {
        "exp": expire,
        "type": token_type,
        "email": email,
        "otp_code": otp_code,
    }
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    return encoded_jwt


def verify_otp_token(token: str) -> dict:
    """
    Verify the JWT OTP token and return the payload.
    Raises exception if invalid or expired.
    """
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        if payload.get("type") not in ["registration", "forgot_password"]:
            raise jwt.PyJWTError("Invalid token type")
        return payload
    except jwt.ExpiredSignatureError:
        raise ValueError("OTP expired")
    except jwt.PyJWTError:
        raise ValueError("Invalid token")

def create_reset_token(email: str, expires_delta: timedelta) -> str:
    """
    Create a short-lived JWT token specifically for resetting the password after OTP is verified.
    """
    expire = datetime.now(timezone.utc) + expires_delta
    to_encode = {
        "exp": expire,
        "type": "reset_password",
        "email": email,
    }
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    return encoded_jwt


def verify_reset_token(token: str) -> dict:
    """
    Verify the JWT reset token and return the payload.
    Raises exception if invalid or expired.
    """
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        if payload.get("type") != "reset_password":
            raise jwt.PyJWTError("Invalid token type")
        return payload
    except jwt.ExpiredSignatureError:
        raise ValueError("Reset token expired")
    except jwt.PyJWTError:
        raise ValueError("Invalid reset token")


def create_access_token(data: dict, expires_delta: timedelta) -> str:
    """
    Create a JWT representing the access token.
    Usually contains user ID.
    """
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + expires_delta
    to_encode.update({"exp": expire, "type": "access"})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    return encoded_jwt


def create_refresh_token(data: dict, expires_delta: timedelta) -> str:
    """
    Create a JWT representing the long-lived refresh token.
    """
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + expires_delta
    to_encode.update({"exp": expire, "type": "refresh"})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    return encoded_jwt


def verify_refresh_token(token: str) -> str:
    """
    Verify the JWT refresh token and return the user_id (sub).
    Raises exception if invalid or expired.
    """
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        if payload.get("type") != "refresh":
            raise jwt.PyJWTError("Invalid token type")
        
        user_id = payload.get("sub")
        if not user_id:
            raise jwt.PyJWTError("Missing subject")
            
        return str(user_id)
    except jwt.ExpiredSignatureError:
        raise ValueError("Refresh token expired")
    except jwt.PyJWTError:
        raise ValueError("Invalid refresh token")
