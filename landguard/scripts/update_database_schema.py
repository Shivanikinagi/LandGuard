"""
Update Database Schema
Migration script to update existing database schema to match current models
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from database import engine, Base
from database.models import User, LandRecord, AnalysisResult, AuditLog
from sqlalchemy import text
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def update_land_records_table():
    """Update land_records table schema"""
    try:
        with engine.connect() as conn:
            # Check if columns exist and add if missing
            columns_to_add = [
                ("user_id", "INTEGER", "REFERENCES users(id)"),
                ("document_type", "VARCHAR(50)", ""),
                ("original_filename", "VARCHAR(255)", ""),
                ("file_path", "VARCHAR(500)", ""),
                ("file_size", "INTEGER", ""),
                ("file_hash", "VARCHAR(64)", ""),
                ("compressed_file_path", "VARCHAR(500)", ""),
                ("encrypted_file_path", "VARCHAR(500)", ""),
                ("compression_ratio", "FLOAT", ""),
                ("ipfs_hash", "VARCHAR(100)", ""),
                ("blockchain_verified", "BOOLEAN", "DEFAULT FALSE"),
                ("transaction_hash", "VARCHAR(100)", ""),
                ("updated_at", "TIMESTAMP WITH TIME ZONE", "")
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
                        if constraint and constraint != "":
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

def update_analysis_results_table():
    """Update analysis_results table schema"""
    try:
        with engine.connect() as conn:
            # Check if columns exist and add if missing
            columns_to_add = [
                ("anomaly_detected", "BOOLEAN", "DEFAULT FALSE"),
                ("anomaly_score", "FLOAT", "DEFAULT 0.0"),
                ("anomaly_types", "JSON", ""),
                ("text_analysis", "JSON", ""),
                ("pattern_analysis", "JSON", ""),
                ("risk_assessment", "VARCHAR(20)", ""),
                ("confidence_score", "FLOAT", ""),
                ("analyzed_by", "INTEGER", "REFERENCES users(id)"),
                ("model_version", "VARCHAR(20)", ""),
                ("updated_at", "TIMESTAMP WITH TIME ZONE", "")
            ]
            
            for col_name, col_type, constraint in columns_to_add:
                try:
                    # Check if column exists
                    check_query = text(f"""
                        SELECT column_name 
                        FROM information_schema.columns 
                        WHERE table_name = 'analysis_results' 
                        AND column_name = '{col_name}'
                    """)
                    
                    result = conn.execute(check_query)
                    if not result.fetchone():
                        # Add column
                        logger.info(f"Adding column: {col_name}")
                        
                        add_query = f"ALTER TABLE analysis_results ADD COLUMN {col_name} {col_type}"
                        if constraint and constraint != "":
                            add_query += f" {constraint}"
                        
                        conn.execute(text(add_query))
                        conn.commit()
                        logger.info(f"✅ Added column: {col_name}")
                    else:
                        logger.info(f"✓ Column exists: {col_name}")
                        
                except Exception as e:
                    logger.error(f"Error adding column {col_name}: {e}")
                    conn.rollback()
            
            logger.info("\n✅ All analysis_results columns checked/added successfully!")
            
    except Exception as e:
        logger.error(f"Error: {e}")
        raise

def main():
    """Main migration function"""
    print("=" * 60)
    print("Updating Database Schema")
    print("=" * 60)
    print()
    
    try:
        update_land_records_table()
        update_analysis_results_table()
        
        print()
        print("=" * 60)
        print("✅ Database schema update completed successfully!")
        print("💡 Note: You may need to restart your backend server.")
        print("=" * 60)
        
    except Exception as e:
        logger.error(f"Migration failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()