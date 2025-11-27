"""
Health Check Routes
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database.connection import get_db

router = APIRouter()


@router.get("/health")
async def health_check():
    """Basic health check"""
    return {
        "status": "healthy",
        "service": "landguard-api",
        "version": "1.0.0"
    }


@router.get("/health/db")
async def database_health(db: Session = Depends(get_db)):
    """Database health check"""
    try:
        # Try to execute a simple query
        db.execute("SELECT 1")
        return {
            "status": "healthy",
            "database": "connected",
            "message": "Database connection is working"
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "database": "disconnected",
            "error": str(e)
        }