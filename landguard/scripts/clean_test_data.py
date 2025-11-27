"""
Clean test data from database.
Run this before tests if you get duplicate key errors.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from database.connection import db_manager
from sqlalchemy import text


def clean_test_data():
    """Remove all test data from database."""
    print("🧹 Cleaning test data from database...")
    
    engine = db_manager.get_pg_engine()
    
    with engine.connect() as conn:
        # Delete test records
        test_patterns = [
            "DELETE FROM analysis_results WHERE land_record_id IN (SELECT id FROM land_records WHERE land_id LIKE 'LND-TEST%' OR land_id LIKE 'LND-SEARCH%' OR land_id LIKE 'LND-ANALYSIS%')",
            "DELETE FROM audit_logs WHERE land_record_id IN (SELECT id FROM land_records WHERE land_id LIKE 'LND-TEST%' OR land_id LIKE 'LND-SEARCH%' OR land_id LIKE 'LND-ANALYSIS%')",
            "DELETE FROM land_records WHERE land_id LIKE 'LND-TEST%' OR land_id LIKE 'LND-SEARCH%' OR land_id LIKE 'LND-ANALYSIS%'",
            "DELETE FROM users WHERE username LIKE 'test_%' OR email LIKE '%test%@landguard.com' OR email LIKE '%@landguard.com' AND username != 'admin'",
        ]
        
        for query in test_patterns:
            result = conn.execute(text(query))
            conn.commit()
            print(f"  ✅ Cleaned: {result.rowcount} rows")
    
    print("✅ Test data cleaned successfully!")


if __name__ == "__main__":
    try:
        clean_test_data()
    except Exception as e:
        print(f"❌ Error cleaning test data: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)