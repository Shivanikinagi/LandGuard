"""
Fix land_records table - Add missing columns
"""

import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import logging

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:Shivani123@localhost:5432/landguard"
)

def add_missing_columns():
    """Add missing columns to land_records table"""
    try:
        engine = create_engine(DATABASE_URL)
        
        with engine.connect() as conn:
            # Check if columns exist and add if missing
            columns_to_add = [
                ("user_id", "INTEGER", "REFERENCES users(id)"),
                ("document_type", "VARCHAR(50)", ""),
                ("area", "FLOAT", ""),
                ("owner_name", "VARCHAR(100)", ""),
                ("location", "VARCHAR(255)", ""),
            ]
            
            for col_name, col_type, constraint in columns_to_add:
                try:
                    # Check if column exists
                    check_query = text(f"""
                        SELECT column_name 
                        FROM information_schema.columns 
                        WHERE table_name = 'land_records' 
                        AND column_name = '{col_name}'
                    """)
                    
                    result = conn.execute(check_query)
                    if not result.fetchone():
                        # Add column
                        logger.info(f"Adding column: {col_name}")
                        
                        add_query = f"ALTER TABLE land_records ADD COLUMN {col_name} {col_type}"
                        if len(constraint) > 0 and constraint != "":
                            add_query += f" {constraint}"
                        
                        conn.execute(text(add_query))
                        conn.commit()
                        logger.info(f"✅ Added column: {col_name}")
                    else:
                        logger.info(f"✓ Column exists: {col_name}")
                        
                except Exception as e:
                    logger.error(f"Error adding column {col_name}: {e}")
                    conn.rollback()
            
            logger.info("\n✅ All columns checked/added successfully!")
            
    except Exception as e:
        logger.error(f"Error: {e}")
        raise

if __name__ == "__main__":
    print("=" * 60)
    print("Adding Missing Columns to land_records Table")
    print("=" * 60)
    print()
    
    add_missing_columns()
    
    print()
    print("=" * 60)
    print("✅ Done! Restart your backend server.")
    print("=" * 60)