"""
Health Check Routes
System health and status endpoints
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from datetime import datetime
from typing import Dict, Any

from database import get_db

router = APIRouter()


@router.get("/health")
async def health_check(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """
    Health check endpoint
    
    Returns:
        System health status
    """
    try:
        # Test database connection with proper text() wrapper
        db.execute(text("SELECT 1"))
        db_status = "connected"
    except Exception as e:
        db_status = f"error: {str(e)}"
    
    return {
        "status": "healthy",
        "database": db_status,
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0"
    }


@router.get("/ping")
async def ping() -> Dict[str, str]:
    """
    Simple ping endpoint
    
    Returns:
        Pong response
    """
    return {
        "message": "pong",
        "timestamp": datetime.utcnow().isoformat()
    }


@router.get("/status")
async def system_status(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """
    Detailed system status
    
    Returns:
        Detailed system information
    """
    status = {
        "api": "running",
        "timestamp": datetime.utcnow().isoformat()
    }
    
    # Check database
    try:
        db.execute(text("SELECT 1"))
        status["database"] = "connected"
    except Exception as e:
        status["database"] = f"error: {str(e)}"
    
    # Check IPFS (optional)
    try:
        from core.blockchain.ipfs_integration import IPFSIntegration
        ipfs = IPFSIntegration()
        status["ipfs"] = "available" if ipfs.handler.ipfs_available else "unavailable"
    except:
        status["ipfs"] = "unavailable"
    
    # Check blockchain (optional)
    try:
        from core.blockchain.blockchain_client import BlockchainClient
        blockchain = BlockchainClient()
        status["blockchain"] = "sandbox_mode" if blockchain.sandbox_mode else "connected"
    except:
        status["blockchain"] = "unavailable"
    
    return status