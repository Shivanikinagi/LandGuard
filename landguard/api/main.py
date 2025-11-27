"""
LandGuard API - Main FastAPI Application
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from contextlib import asynccontextmanager
import logging

from api.routes import auth, analysis, upload, health, statistics
from api.middleware import setup_middleware
from database.connection import engine, Base

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    logger.info("Starting LandGuard API...")
    
    # Create database tables
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Error creating database tables: {e}")
    
    yield
    
    # Shutdown
    logger.info("Shutting down LandGuard API...")


# Create FastAPI app
app = FastAPI(
    title="LandGuard API",
    description="AI-Powered Land Fraud Detection System",
    version="1.0.0",
    lifespan=lifespan
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Gzip Compression
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Custom middleware
setup_middleware(app)

# Include routers
app.include_router(health.router, prefix="/api", tags=["Health"])
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(statistics.router, prefix="/api/statistics", tags=["Statistics"])
app.include_router(analysis.router, prefix="/api/analysis", tags=["Analysis"])
app.include_router(upload.router, prefix="/api/upload", tags=["Upload"])


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "LandGuard API",
        "version": "1.0.0",
        "status": "running"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )