"""
Simple Test Script
Minimal script to test database connection and API components
"""

import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

print("Starting simple test...")

# Test database connection
try:
    from database.connection import check_db_connection
    if check_db_connection():
        print("✅ Database connection successful")
    else:
        print("❌ Database connection failed")
except Exception as e:
    print(f"❌ Database connection error: {e}")

# Test model imports
try:
    from database.models import User, LandRecord, AnalysisResult, AuditLog
    print("✅ Database models imported successfully")
except Exception as e:
    print(f"❌ Database models import error: {e}")

print("Simple test completed!")