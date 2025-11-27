"""
FastAPI Main Application
Entry point for the LandGuard API
"""

import os
import sys
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
from dotenv import load_dotenv

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Import routes
from api.routes import auth, upload, analysis, blockchain, dashboard, statistics, processing

# Create FastAPI app
app = FastAPI(
    title="LandGuard API",
    description="AI-powered land document management system with fraud detection",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS configuration
origins = os.getenv("CORS_ORIGINS", "http://localhost:5173,http://localhost:3000").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(upload.router, prefix="/upload", tags=["upload"])
app.include_router(analysis.router, prefix="/analysis", tags=["analysis"])
app.include_router(blockchain.router, prefix="/blockchain", tags=["blockchain"])
app.include_router(dashboard.router, prefix="/dashboard", tags=["dashboard"])
app.include_router(statistics.router, prefix="/statistics", tags=["statistics"])
app.include_router(processing.router, prefix="/processing", tags=["processing"])

@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "Welcome to LandGuard API"}

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
