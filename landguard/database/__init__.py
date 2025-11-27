"""
Database Package
Handles database connections, models, and operations
"""

from .connection import Base, engine, SessionLocal, get_db, create_tables, check_db_connection
from .models import User, LandRecord, AnalysisResult, AuditLog

from .auth import (
    hash_password,
    verify_password,
    create_access_token,
    decode_access_token,
    create_api_key,
    verify_api_key
)

__all__ = [
    # Connection
    "Base",
    "engine",
    "SessionLocal",
    "get_db",
    "create_tables",
    "check_db_connection",
    
    # Models
    "User",
    "LandRecord",
    "AnalysisResult",
    "AuditLog",
    
    # Auth
    "hash_password",
    "verify_password",
    "create_access_token",
    "decode_access_token",
    "create_api_key",
    "verify_api_key"
]