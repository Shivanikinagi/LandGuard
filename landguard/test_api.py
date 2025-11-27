"""
Test API Script
Simple script to test if the API components work correctly
"""

import sys
import os
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Now we can import the database module
try:
    from database import check_db_connection, engine, Base
    from database.models import User, LandRecord, AnalysisResult, AuditLog
    print("✅ Database modules imported successfully")
    
    # Test database connection
    if check_db_connection():
        print("✅ Database connection successful")
    else:
        print("❌ Database connection failed")
        
except Exception as e:
    print(f"❌ Error importing database modules: {e}")
    import traceback
    traceback.print_exc()

# Test API routes
try:
    from api.routes import auth, upload, analysis, blockchain, dashboard, statistics
    print("✅ API routes imported successfully")
except Exception as e:
    print(f"❌ Error importing API routes: {e}")
    import traceback
    traceback.print_exc()

print("\n🎉 Test script completed!")