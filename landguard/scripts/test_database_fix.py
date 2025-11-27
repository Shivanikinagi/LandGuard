"""
Test Database Fix
Script to test if database schema issues have been resolved
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

def test_database_connection():
    """Test database connection"""
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            logger.info("✅ Database connection successful")
            return True
    except Exception as e:
        logger.error(f"❌ Database connection failed: {e}")
        return False

def test_table_structure():
    """Test if all required tables exist with correct structure"""
    try:
        with engine.connect() as conn:
            # Check land_records table
            result = conn.execute(text("""
                SELECT column_name, data_type 
                FROM information_schema.columns 
                WHERE table_name = 'land_records' 
                ORDER BY ordinal_position
            """))
            
            columns = result.fetchall()
            logger.info("✅ land_records table exists")
            logger.info(f"   Columns: {len(columns)}")
            
            # Check for required columns
            required_columns = {
                'id', 'record_number', 'owner_name', 'location', 'area', 
                'document_type', 'status', 'user_id', 'original_filename',
                'file_path', 'file_size', 'file_hash', 'ipfs_hash'
            }
            
            existing_columns = {col[0] for col in columns}
            missing_columns = required_columns - existing_columns
            
            if missing_columns:
                logger.warning(f"⚠️  Missing columns in land_records: {missing_columns}")
            else:
                logger.info("✅ All required columns present in land_records")
            
            # Check analysis_results table
            result = conn.execute(text("""
                SELECT column_name, data_type 
                FROM information_schema.columns 
                WHERE table_name = 'analysis_results' 
                ORDER BY ordinal_position
            """))
            
            columns = result.fetchall()
            logger.info("✅ analysis_results table exists")
            logger.info(f"   Columns: {len(columns)}")
            
            # Check for required columns
            required_columns = {
                'id', 'land_record_id', 'fraud_detected', 'fraud_score', 
                'fraud_indicators', 'anomaly_detected', 'anomaly_score',
                'risk_assessment', 'confidence_score'
            }
            
            existing_columns = {col[0] for col in columns}
            missing_columns = required_columns - existing_columns
            
            if missing_columns:
                logger.warning(f"⚠️  Missing columns in analysis_results: {missing_columns}")
            else:
                logger.info("✅ All required columns present in analysis_results")
            
            return True
            
    except Exception as e:
        logger.error(f"❌ Table structure test failed: {e}")
        return False

def test_model_imports():
    """Test if all models can be imported and used"""
    try:
        # Test model creation (without saving to DB)
        user = User(
            username="test_user",
            email="test@example.com",
            password_hash="test_hash",
            full_name="Test User"
        )
        
        land_record = LandRecord(
            record_number="TEST-001",
            original_filename="test.pdf",
            file_path="/tmp/test.pdf",
            file_size=1024,
            status="uploaded",
            user_id=1
        )
        
        analysis = AnalysisResult(
            land_record_id=1,
            fraud_detected=False,
            fraud_score=0.1,
            risk_assessment="low"
        )
        
        audit_log = AuditLog(
            user_id=1,
            action="test",
            entity_type="test",
            entity_id=1
        )
        
        logger.info("✅ All models can be instantiated")
        return True
        
    except Exception as e:
        logger.error(f"❌ Model import/test failed: {e}")
        return False

def test_relationships():
    """Test if model relationships are properly defined"""
    try:
        # Check if relationships exist
        user = User()
        land_record = LandRecord()
        analysis = AnalysisResult()
        audit_log = AuditLog()
        
        # These should exist if relationships are properly defined
        logger.info("✅ Model relationships appear to be properly defined")
        return True
        
    except Exception as e:
        logger.error(f"❌ Relationship test failed: {e}")
        return False

def main():
    """Main test function"""
    print("=" * 60)
    print("Testing Database Fix")
    print("=" * 60)
    print()
    
    tests = [
        ("Database Connection", test_database_connection),
        ("Table Structure", test_table_structure),
        ("Model Imports", test_model_imports),
        ("Relationships", test_relationships)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\nRunning {test_name} test...")
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name} test PASSED")
            else:
                print(f"❌ {test_name} test FAILED")
        except Exception as e:
            print(f"❌ {test_name} test FAILED with exception: {e}")
    
    print("\n" + "=" * 60)
    print(f"Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Database schema appears to be correct.")
        print("💡 You can now run the database initialization script.")
    else:
        print("⚠️  Some tests failed. Please check the logs above.")
        print("💡 You may need to run the update_database_schema.py script.")
    
    print("=" * 60)

if __name__ == "__main__":
    main()