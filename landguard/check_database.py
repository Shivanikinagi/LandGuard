"""
Check Database Schema
Verify what columns actually exist in the users table
"""

import os
from sqlalchemy import create_engine, text, inspect
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Get DATABASE_URL from .env file or use default with correct password
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:Shivani123@localhost:5432/landguard"
)

def check_database_schema():
    """Check what columns exist in users table"""
    try:
        engine = create_engine(DATABASE_URL)
        inspector = inspect(engine)
        
        # Get columns for users table
        if 'users' in inspector.get_table_names():
            columns = inspector.get_columns('users')
            
            print("\n" + "=" * 60)
            print("USERS TABLE COLUMNS:")
            print("=" * 60)
            
            for col in columns:
                print(f"  - {col['name']} ({col['type']})")
            
            print("=" * 60 + "\n")
            
            # Check specifically for password-related columns
            col_names = [col['name'] for col in columns]
            
            if 'password' in col_names:
                print("✅ Found 'password' column")
                print("\n📝 Action: Model should use 'password' field")
                return 'password'
            elif 'hashed_password' in col_names:
                print("✅ Found 'hashed_password' column")
                print("\n📝 Action: Model should use 'hashed_password' field (already updated)")
                return 'hashed_password'
            else:
                print("❌ No password column found!")
                return None
        else:
            print("❌ Users table does not exist!")
            print("\nCreating tables...")
            
            # Try to create tables
            from database.connection import Base, engine as db_engine
            from database.models import User, LandRecord, AnalysisResult, AuditLog
            
            Base.metadata.create_all(bind=db_engine)
            print("✅ Tables created! Run this script again.")
            return None
            
    except Exception as e:
        logger.error(f"Error checking database: {e}")
        print(f"\n❌ Error: {e}")
        print("\nTroubleshooting:")
        print("1. Verify PostgreSQL is running")
        print("2. Check .env file has correct DATABASE_URL")
        print("3. Verify password is correct: Shivani123")
        return None

if __name__ == "__main__":
    print("=" * 60)
    print("PostgreSQL Database Schema Checker")
    print("=" * 60)
    print(f"\nConnecting to: {DATABASE_URL.split('@')[1]}")  # Hide password
    print()
    
    result = check_database_schema()
    
    if result == 'password':
        print("\n" + "=" * 60)
        print("Next Step: Update model to use 'password'")
        print("=" * 60)
    elif result == 'hashed_password':
        print("\n" + "=" * 60)
        print("✅ Model already matches database schema!")
        print("=" * 60)
        print("\nJust restart backend:")
        print("python -m uvicorn api.main:app --reload")
    else:
        print("\n" + "=" * 60)
        print("❌ Cannot proceed - fix database connection first")
        print("=" * 60)