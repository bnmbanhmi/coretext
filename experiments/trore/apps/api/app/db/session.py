from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os

# Use an env var or default to sqlite for now if not set
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./trore.db")

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    # connect_args is needed for SQLite
    connect_args={"check_same_thread": False} if "sqlite" in SQLALCHEMY_DATABASE_URL else {}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
