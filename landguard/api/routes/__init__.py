"""
API Routes Package
Registers all API route modules
"""

from .auth import router as auth_router
from .upload import router as upload_router
from .analysis import router as analysis_router
from .statistics import router as statistics_router
from .dashboard import router as dashboard_router
from .health import router as health_router
from .blockchain import router as blockchain_router
from .processing import router as processing_router

__all__ = [
    "auth_router",
    "upload_router",
    "analysis_router",
    "statistics_router",
    "dashboard_router",
    "health_router",
    "blockchain_router",
    "processing_router"
]