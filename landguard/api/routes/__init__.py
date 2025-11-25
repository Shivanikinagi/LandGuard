"""
API routes for LandGuard.
"""

from .health import router as health_router
from .auth import router as auth_router
from .analysis import router as analysis_router
from .upload import router as upload_router

__all__ = [
    'health_router',
    'auth_router',
    'analysis_router',
    'upload_router',
]