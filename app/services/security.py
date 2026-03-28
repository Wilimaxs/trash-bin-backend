import bcrypt


def hash_password(password: str) -> str:
    encoded = password.encode("utf-8")
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(encoded, salt).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    encoded = plain_password.encode("utf-8")
    return bcrypt.checkpw(encoded, hashed_password.encode("utf-8"))