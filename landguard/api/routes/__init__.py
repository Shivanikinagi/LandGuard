"""
API Routes Package
"""

from .auth import router as auth_router
from .analysis import router as analysis_router
from .upload import router as upload_router
from .health import router as health_router
from .statistics import router as statistics_router

__all__ = [
    'auth_router',
    'analysis_router',
    'upload_router',
    'health_router',
    'statistics_router',
]