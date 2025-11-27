"""
Database Connection Management
PostgreSQL Configuration with SQLAlchemy
"""

from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database Configuration
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:postgres@localhost:5432/landguard"
)

# Create SQLAlchemy engine
engine = create_engine(
    DATABASE_URL,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,
    pool_recycle=3600,
    echo=False  # Set to True for SQL debugging
)

# Create SessionLocal class
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# Create Base class for models
Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """
    Database dependency for FastAPI
    Provides a database session and ensures it's closed after use
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    """
    Initialize database - create all tables
    """
    from database.models import User, LandRecord, Analysis, AuditLog
    Base.metadata.create_all(bind=engine)


def check_db_connection() -> bool:
    """
    Check if database connection is working
    """
    try:
        db = SessionLocal()
        db.execute(text("SELECT 1"))
        db.close()
        return True
    except Exception as e:
        print(f"Database connection error: {e}")
        return False


# Export all
__all__ = [
    'engine',
    'Base',
    'SessionLocal',
    'get_db',
    'init_db',
    'check_db_connection',
]