"""
Start Server Script
Simple script to start the FastAPI server with proper imports
"""

import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

print("Starting LandGuard API server...")

try:
    import uvicorn
    from api.main import app
    
    if __name__ == "__main__":
        uvicorn.run(
            "api.main:app",
            host="0.0.0.0",
            port=8000,
            reload=True,
            log_level="info"
        )
        
except Exception as e:
    print(f"Error starting server: {e}")
    import traceback
    traceback.print_exc()