from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import DATABASE_URL

connect_args = {}
if DATABASE_URL.startswith("sqlite"):
    connect_args["check_same_thread"] = False

# connect to DB using sqlalchemy engine
engine = create_engine(DATABASE_URL, echo=False, future=True, connect_args=connect_args)

# action for creating a session with
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)
