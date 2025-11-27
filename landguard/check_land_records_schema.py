"""
Check land_records table schema
"""

import os
from sqlalchemy import create_engine, inspect
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:Shivani123@localhost:5432/landguard"
)

def check_land_records_schema():
    """Check what columns exist in land_records table"""
    try:
        engine = create_engine(DATABASE_URL)
        inspector = inspect(engine)
        
        print("\n" + "=" * 60)
        print("LAND_RECORDS TABLE SCHEMA")
        print("=" * 60)
        
        if 'land_records' in inspector.get_table_names():
            columns = inspector.get_columns('land_records')
            
            print("\nColumns found:")
            for col in columns:
                print(f"  - {col['name']:30} {col['type']}")
            
            print("\n" + "=" * 60)
            
            # Check for foreign keys
            fks = inspector.get_foreign_keys('land_records')
            if fks:
                print("\nForeign Keys:")
                for fk in fks:
                    print(f"  - {fk['constrained_columns']} -> {fk['referred_table']}.{fk['referred_columns']}")
            else:
                print("\n⚠️  No foreign keys found")
            
            print("=" * 60)
        else:
            print("\n❌ land_records table does not exist!")
            print("\nAvailable tables:")
            for table in inspector.get_table_names():
                print(f"  - {table}")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")

if __name__ == "__main__":
    check_land_records_schema()