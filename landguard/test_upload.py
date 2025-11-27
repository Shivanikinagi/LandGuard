"""
Test Upload Functionality
Simple script to test the upload functionality directly
"""

import sys
from pathlib import Path
import os
import tempfile

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

print("Testing upload functionality...")

try:
    # Create a test file
    test_content = "This is a test document for LandGuard upload testing."
    
    # Create a temporary file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write(test_content)
        test_file_path = f.name
    
    print(f"Created test file: {test_file_path}")
    
    # Test the upload functionality directly
    from database import get_db, engine, Base
    from database.models import User, LandRecord
    from database.connection import check_db_connection
    from sqlalchemy.orm import Session
    
    # Check database connection
    if check_db_connection():
        print("✅ Database connection successful")
        
        # Get a database session
        db_generator = get_db()
        db = next(db_generator)
        
        try:
            # Get a test user (use the one we know exists)
            user = db.query(User).first()
            if user:
                print(f"✅ Found user: {user.username} (ID: {user.id})")
                
                # Test creating a LandRecord directly
                import hashlib
                from datetime import datetime
                
                # Calculate file hash
                file_hash = hashlib.sha256(test_content.encode()).hexdigest()
                
                # Generate unique filename
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                unique_filename = f"{timestamp}_test-document.txt"
                file_path = os.path.join("uploads", unique_filename)
                
                # Save file
                os.makedirs("uploads", exist_ok=True)
                with open(file_path, "w") as f:
                    f.write(test_content)
                
                print(f"✅ Saved file to: {file_path}")
                
                # Create database record
                record = LandRecord(
                    record_number=f"REC-{timestamp}-{user.id}",
                    original_filename="test-document.txt",
                    file_path=file_path,
                    file_size=len(test_content),
                    file_hash=file_hash,
                    status="uploaded",
                    user_id=user.id
                )
                
                db.add(record)
                db.commit()
                db.refresh(record)
                
                print(f"✅ Created database record: {record.record_number} (ID: {record.id})")
                print("🎉 Upload test completed successfully!")
                
                # Clean up
                db.delete(record)
                db.commit()
                os.remove(file_path)
                print("✅ Cleaned up test data")
                
            else:
                print("❌ No users found in database")
                
        except Exception as e:
            print(f"❌ Error during upload test: {e}")
            import traceback
            traceback.print_exc()
        finally:
            # Close database session
            try:
                next(db_generator)
            except:
                pass
    else:
        print("❌ Database connection failed")
        
    # Clean up test file
    if os.path.exists(test_file_path):
        os.remove(test_file_path)
        print(f"✅ Cleaned up temporary file: {test_file_path}")
        
except Exception as e:
    print(f"❌ Error in upload test: {e}")
    import traceback
    traceback.print_exc()

print("Upload test completed!")