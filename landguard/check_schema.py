"""
Check Schema Script
Simple script to check the database schema
"""

import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from database import engine
from sqlalchemy import text

print("Checking land_records table schema...")

try:
    with engine.connect() as conn:
        # Check owner_name column
        result = conn.execute(text("""
            SELECT column_name, is_nullable, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'land_records' 
            AND column_name = 'owner_name'
        """))
        row = result.fetchone()
        if row:
            print(f"owner_name column: nullable={row[1]}, type={row[2]}")
        else:
            print("owner_name column not found")
            
        # Check all columns
        result = conn.execute(text("""
            SELECT column_name, is_nullable, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'land_records' 
            ORDER BY ordinal_position
        """))
        print("\nAll columns in land_records table:")
        for row in result.fetchall():
            nullable = "NULL" if row[1] == "YES" else "NOT NULL"
            print(f"  {row[0]:20s} {nullable:8s} {row[2]}")
            
except Exception as e:
    print(f"Error checking schema: {e}")
    import traceback
    traceback.print_exc()

print("Schema check completed!")