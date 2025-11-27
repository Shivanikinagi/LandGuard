"""
Fix Database Column Name
Renames hashed_password to password in users table
"""

import os
from sqlalchemy import create_engine, text
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database URL (same as backend uses)
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:postgres@localhost:5432/landguard"
)

def fix_column_name():
    """Rename hashed_password column to password"""
    try:
        # Create engine
        engine = create_engine(DATABASE_URL)
        
        # Connect and execute
        with engine.connect() as conn:
            # Check if column exists
            check_query = text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'users' 
                AND column_name = 'hashed_password'
            """)
            
            result = conn.execute(check_query)
            if result.fetchone():
                logger.info("Found 'hashed_password' column, renaming to 'password'...")
                
                # Rename column
                rename_query = text("""
                    ALTER TABLE users 
                    RENAME COLUMN hashed_password TO password
                """)
                
                conn.execute(rename_query)
                conn.commit()
                
                logger.info("✅ Column renamed successfully!")
                return True
            else:
                logger.info("Column 'hashed_password' not found. Checking for 'password'...")
                
                # Check if password column already exists
                check_password = text("""
                    SELECT column_name 
                    FROM information_schema.columns 
                    WHERE table_name = 'users' 
                    AND column_name = 'password'
                """)
                
                result = conn.execute(check_password)
                if result.fetchone():
                    logger.info("✅ Column 'password' already exists!")
                    return True
                else:
                    logger.error("❌ Neither 'hashed_password' nor 'password' column found!")
                    return False
                    
    except Exception as e:
        logger.error(f"❌ Error fixing column: {e}")
        return False

if __name__ == "__main__":
    print("=" * 50)
    print("Database Column Fix Script")
    print("=" * 50)
    print(f"Database URL: {DATABASE_URL}")
    print()
    
    success = fix_column_name()
    
    if success:
        print()
        print("=" * 50)
        print("✅ Database fix completed successfully!")
        print("=" * 50)
        print()
        print("Next steps:")
        print("1. Restart your backend server")
        print("2. Run the test script: .\\test-complete-system.ps1")
    else:
        print()
        print("=" * 50)
        print("❌ Database fix failed!")
        print("=" * 50)
        print()
        print("Alternative solution:")
        print("Keep using 'hashed_password' in the model (already updated)")
        print("Just restart backend: python -m uvicorn api.main:app --reload")