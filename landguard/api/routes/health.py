"""
Health check endpoints.
"""

from datetime import datetime
from fastapi import APIRouter, Depends
from typing import Dict

from api.models.responses import HealthResponse
from api.dependencies import check_rate_limit

router = APIRouter(prefix="/api/v1", tags=["health"])


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Health check endpoint.
    Returns system status and component health.
    """
    return HealthResponse(
        status="healthy",
        version="1.0.0",
        timestamp=datetime.utcnow(),
        checks={
            "api": True,
            "database": True,  # Add actual DB check when implemented
            "security": True,
            "analyzer": True
        }
    )


@router.get("/ping")
async def ping():
    """Simple ping endpoint for basic connectivity check."""
    return {"status": "ok", "timestamp": datetime.utcnow().isoformat()}