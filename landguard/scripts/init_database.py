"""
Initialize Database with Sample Data
PostgreSQL Configuration
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import from database package
from database import (
    SessionLocal,
    engine,
    Base,
    check_db_connection,
    User,
    LandRecord,
    AnalysisResult,
    AuditLog
)

from passlib.context import CryptContext
from datetime import datetime
import random

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_password_hash(password: str) -> str:
    """Hash password"""
    return pwd_context.hash(password)


def create_tables():
    """Create all database tables"""
    print("\n" + "="*60)
    print("Creating database tables...")
    print("="*60)
    
    try:
        Base.metadata.create_all(bind=engine)
        print("✓ Tables created successfully")
        
        # Show created tables
        from sqlalchemy import inspect
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        print(f"  Tables: {', '.join(tables)}")
        
        return True
    except Exception as e:
        print(f"✗ Error creating tables: {e}")
        import traceback
        traceback.print_exc()
        return False


def create_users(db):
    """Create sample users"""
    print("\n" + "="*60)
    print("Creating sample users...")
    print("="*60)
    
    users = [
        {
            "username": "admin",
            "email": "admin@landguard.com",
            "password": "admin123",
            "role": "ADMIN",
            "full_name": "Admin User"
        },
        {
            "username": "analyst",
            "email": "analyst@landguard.com",
            "password": "analyst123",
            "role": "ANALYST",
            "full_name": "Analyst User"
        },
        {
            "username": "viewer",
            "email": "viewer@landguard.com",
            "password": "viewer123",
            "role": "VIEWER",
            "full_name": "Viewer User"
        }
    ]
    
    created_count = 0
    for user_data in users:
        try:
            existing_user = db.query(User).filter(
                User.username == user_data["username"]
            ).first()
            
            if not existing_user:
                user = User(
                    username=user_data["username"],
                    email=user_data["email"],
                    password_hash=get_password_hash(user_data["password"]),
                    role=user_data["role"],
                    full_name=user_data["full_name"],
                    is_active=True
                )
                db.add(user)
                db.commit()
                print(f"  ✓ Created user: {user_data['username']} ({user_data['role']})")
                created_count += 1
            else:
                print(f"  - User already exists: {user_data['username']}")
        except Exception as e:
            print(f"  ✗ Error creating user {user_data['username']}: {e}")
            db.rollback()
    
    print(f"\n✓ Created {created_count} new users")


def create_sample_land_records(db):
    """Create sample land records"""
    print("\n" + "="*60)
    print("Creating sample land records...")
    print("="*60)
    
    locations = [
        "Mumbai, Maharashtra",
        "Delhi, Delhi",
        "Bangalore, Karnataka",
        "Chennai, Tamil Nadu",
        "Kolkata, West Bengal",
        "Hyderabad, Telangana",
        "Pune, Maharashtra",
        "Ahmedabad, Gujarat",
        "Jaipur, Rajasthan",
        "Lucknow, Uttar Pradesh"
    ]
    
    created_count = 0
    for i in range(50):
        record_number = f"LR-2024-{str(i + 1).zfill(4)}"
        
        try:
            existing_record = db.query(LandRecord).filter(
                LandRecord.record_number == record_number
            ).first()
            
            if not existing_record:
                land_record = LandRecord(
                    record_number=record_number,
                    owner_name=f"Owner {i + 1}",
                    location=random.choice(locations),
                    area=round(random.uniform(100, 5000), 2),
                    status="PENDING"
                )
                db.add(land_record)
                db.commit()
                
                created_count += 1
                if created_count % 10 == 0:
                    print(f"  ✓ Created {created_count} land records...")
        except Exception as e:
            print(f"  ✗ Error creating land record {record_number}: {e}")
            db.rollback()
    
    print(f"\n✓ Created {created_count} new land records")


def create_sample_analyses(db):
    """Create sample analysis results"""
    print("\n" + "="*60)
    print("Creating sample analyses...")
    print("="*60)
    
    land_records = db.query(LandRecord).limit(30).all()
    risk_levels = ["HIGH", "MEDIUM", "LOW"]
    
    created_count = 0
    for record in land_records:
        try:
            existing_analysis = db.query(AnalysisResult).filter(
                AnalysisResult.land_record_id == record.id
            ).first()
            
            if not existing_analysis:
                risk_level = random.choice(risk_levels)
                fraud_prob = {
                    "HIGH": random.uniform(0.7, 0.95),
                    "MEDIUM": random.uniform(0.4, 0.7),
                    "LOW": random.uniform(0.1, 0.4)
                }[risk_level]
                
                flags = []
                if risk_level == "HIGH":
                    flags = [
                        "Duplicate ownership detected",
                        "Price anomaly identified",
                        "Document verification failed"
                    ]
                elif risk_level == "MEDIUM":
                    flags = ["Minor discrepancy in documentation"]
                
                analysis = AnalysisResult(
                    land_record_id=record.id,
                    fraud_detected=risk_level in ["HIGH", "MEDIUM"],
                    fraud_score=round(fraud_prob, 2),
                    fraud_indicators=flags,
                    risk_assessment=risk_level,
                    confidence_score=round(random.uniform(0.8, 0.95), 2)
                )
                db.add(analysis)
                
                # Update land record status
                record.status = "ANALYZED"
                
                db.commit()
                created_count += 1
                
                if created_count % 10 == 0:
                    print(f"  ✓ Created {created_count} analyses...")
        except Exception as e:
            print(f"  ✗ Error creating analysis for record {record.record_number}: {e}")
            db.rollback()
    
    print(f"\n✓ Created {created_count} new analyses")


def main():
    """Main initialization function"""
    print("\n" + "="*60)
    print("  LandGuard Database Initialization")
    print("  PostgreSQL Configuration")
    print("="*60)
    
    # Check database connection
    print("\nStep 1: Checking database connection...")
    if not check_db_connection():
        print("\n✗ Cannot connect to database!")
        print("\nPlease ensure:")
        print("  1. PostgreSQL is running")
        print("  2. Database 'landguard' exists")
        print("  3. Connection settings in .env are correct")
        print("\nTo create the database:")
        print("  psql -U postgres")
        print("  CREATE DATABASE landguard;")
        print("  \\q")
        return
    
    print("✓ Database connection successful")
    
    # Create tables
    print("\nStep 2: Creating database tables...")
    if not create_tables():
        return
    
    # Create database session
    db = SessionLocal()
    
    try:
        # Create users
        print("\nStep 3: Creating users...")
        create_users(db)
        
        # Create sample data
        print("\nStep 4: Creating sample land records...")
        create_sample_land_records(db)
        
        print("\nStep 5: Creating sample analyses...")
        create_sample_analyses(db)
        
        print("\n" + "="*60)
        print("✓ Database initialization completed successfully!")
        print("="*60)
        print("\nDatabase Summary:")
        print(f"  Users: {db.query(User).count()}")
        print(f"  Land Records: {db.query(LandRecord).count()}")
        print(f"  Analyses: {db.query(AnalysisResult).count()}")
        print("\nSample credentials:")
        print("  Admin:   admin / admin123")
        print("  Analyst: analyst / analyst123")
        print("  Viewer:  viewer / viewer123")
        print("\n" + "="*60)
        
    except Exception as e:
        print(f"\n✗ Error during initialization: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    main()