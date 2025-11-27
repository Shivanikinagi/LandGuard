"""
Database Connection
SQLAlchemy database connection and session management
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import logging

# Load environment variables from .env file
load_dotenv()

# Configure logging
logger = logging.getLogger(__name__)

# Database URL from environment variable
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:Shivani123@localhost:5432/landguard"  # Updated default
)

logger.info(f"Connecting to database: {DATABASE_URL.split('@')[1]}")  # Log only host/db, not password

# Create SQLAlchemy engine
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
    echo=False  # Set to True for SQL query logging
)

# Create SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create Base class for models
Base = declarative_base()


def get_db():
    """
    Dependency for getting database session
    
    Yields:
        Database session
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_tables():
    """
    Create all database tables
    
    This function creates all tables defined in the models
    """
    try:
        # Import all models to ensure they are registered
        from database.models import User, LandRecord, AnalysisResult, AuditLog
        
        # Create all tables
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
        
    except Exception as e:
        logger.error(f"Error creating database tables: {e}")
        raise


def drop_tables():
    """
    Drop all database tables (use with caution!)
    """
    try:
        Base.metadata.drop_all(bind=engine)
        logger.warning("All database tables dropped")
    except Exception as e:
        logger.error(f"Error dropping database tables: {e}")
        raise


def check_db_connection():
    """
    Check if database connection is working
    
    Returns:
        bool: True if connection works, False otherwise
    """
    try:
        from sqlalchemy import text
        db = SessionLocal()
        db.execute(text("SELECT 1"))
        db.close()
        return True
    except Exception as e:
        logger.error(f"Database connection error: {e}")
        return False


def reset_database():
    """
    Reset database by dropping and recreating all tables
    WARNING: This will delete all data!
    """
    try:
        drop_tables()
        create_tables()
        logger.info("Database reset successfully")
    except Exception as e:
        logger.error(f"Error resetting database: {e}")
        raise
