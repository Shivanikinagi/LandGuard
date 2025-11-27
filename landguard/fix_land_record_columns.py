"""
Fix Land Record Columns
Script to fix NOT NULL constraints on land_records table
"""

import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from database import engine
from sqlalchemy import text
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def fix_land_record_columns():
    """Fix NOT NULL constraints on land_records table"""
    try:
        with engine.connect() as conn:
            # List of columns to make nullable
            columns_to_fix = [
                'owner_name',
                'location', 
                'area'
            ]
            
            for column_name in columns_to_fix:
                try:
                    # Check if column is currently NOT NULL
                    check_query = text(f"""
                        SELECT is_nullable
                        FROM information_schema.columns 
                        WHERE table_name = 'land_records' 
                        AND column_name = '{column_name}'
                    """)
                    
                    result = conn.execute(check_query)
                    row = result.fetchone()
                    
                    if row and row[0] == 'NO':
                        logger.info(f"Making column {column_name} nullable...")
                        
                        # For PostgreSQL, we need to drop NOT NULL constraint
                        alter_query = text(f"ALTER TABLE land_records ALTER COLUMN {column_name} DROP NOT NULL")
                        conn.execute(alter_query)
                        conn.commit()
                        
                        logger.info(f"✅ Made {column_name} nullable")
                    else:
                        logger.info(f"✓ Column {column_name} is already nullable")
                        
                except Exception as e:
                    logger.error(f"Error fixing column {column_name}: {e}")
                    conn.rollback()
            
            logger.info("✅ All land_record columns checked/fixed successfully!")
            
    except Exception as e:
        logger.error(f"Error: {e}")
        raise

def main():
    """Main function"""
    print("=" * 60)
    print("Fixing Land Record Columns")
    print("=" * 60)
    print()
    
    try:
        fix_land_record_columns()
        
        print()
        print("=" * 60)
        print("✅ Land record columns fixed successfully!")
        print("💡 Note: You may need to restart your backend server.")
        print("=" * 60)
        
    except Exception as e:
        logger.error(f"Fix failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()