"""
Database setup script.
Creates tables and initializes default data.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from database import db_manager, UserRole
from database.repositories import UserRepository
import bcrypt
from sqlalchemy import text


def test_connection():
    """Test database connection before proceeding."""
    print("🔌 Testing database connections...")
    
    # Test PostgreSQL
    try:
        engine = db_manager.get_pg_engine()
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            assert result.fetchone()[0] == 1
        print("✅ PostgreSQL connection successful")
    except Exception as e:
        print(f"❌ PostgreSQL connection failed: {e}")
        print("\n📝 Troubleshooting steps:")
        print("  1. Check if PostgreSQL is running:")
        print("     Get-Service postgresql*")
        print("  2. Verify config/database.yaml has correct credentials")
        print("  3. Create database manually:")
        print("     psql -U postgres")
        print("     CREATE DATABASE landguard;")
        print("     CREATE USER landguard_user WITH PASSWORD 'your_password';")
        print("     GRANT ALL PRIVILEGES ON DATABASE landguard TO landguard_user;")
        sys.exit(1)
    
    # Test MongoDB (optional)
    try:
        mongo_db = db_manager.get_mongo_db()
        mongo_db.command('ping')
        print("✅ MongoDB connection successful")
    except Exception as e:
        print(f"⚠️  MongoDB connection failed (optional): {e}")
        print("   MongoDB features will be unavailable")


def create_tables():
    """Create all database tables."""
    print("\n📊 Creating database tables...")
    try:
        db_manager.create_pg_tables()
        print("✅ Tables created successfully")
        
        # Verify tables were created
        engine = db_manager.get_pg_engine()
        with engine.connect() as conn:
            result = conn.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
                ORDER BY table_name
            """))
            tables = [row[0] for row in result]
            print(f"   Created tables: {', '.join(tables)}")
    except Exception as e:
        print(f"❌ Error creating tables: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


def create_default_admin():
    """Create default admin user."""
    print("\n👤 Creating default admin user...")
    
    session = db_manager.get_pg_session()
    user_repo = UserRepository(session)
    
    try:
        # Check if admin exists
        existing_admin = user_repo.get_by_username('admin')
        if existing_admin:
            print("⏭️  Admin user already exists")
            print(f"   Username: {existing_admin.username}")
            print(f"   Email: {existing_admin.email}")
            return
        
        # Hash password using bcrypt directly
        password = 'admin123'
        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
        
        # Create admin
        admin_data = {
            'username': 'admin',
            'email': 'admin@landguard.com',
            'hashed_password': hashed_password.decode('utf-8'),
            'full_name': 'System Administrator',
            'role': UserRole.ADMIN,
            'is_active': True
        }
        
        admin = user_repo.create(admin_data)
        print(f"✅ Admin user created successfully")
        print(f"   Username: {admin.username}")
        print(f"   Email: {admin.email}")
        print(f"   Password: admin123")
        print("\n⚠️  IMPORTANT: Change the default password immediately!")
        
    except Exception as e:
        print(f"❌ Error creating admin: {e}")
        import traceback
        traceback.print_exc()
    finally:
        session.close()


def create_mongodb_indexes():
    """Create MongoDB indexes for better performance."""
    print("\n📇 Creating MongoDB indexes...")
    
    try:
        mongo_db = db_manager.get_mongo_db()
        documents_collection = mongo_db['documents']
        
        # Create indexes
        documents_collection.create_index('land_id')
        documents_collection.create_index('document_type')
        documents_collection.create_index([('land_id', 1), ('document_type', 1)])
        
        print("✅ MongoDB indexes created successfully")
    except Exception as e:
        print(f"⚠️  MongoDB indexes skipped: {e}")
        print("   MongoDB features will be unavailable")


def main():
    """Main setup function."""
    print("=" * 60)
    print("🚀 LandGuard Database Setup")
    print("=" * 60)
    
    # Step 0: Test connections first
    test_connection()
    
    # Step 1: Create tables
    create_tables()
    
    # Step 2: Create default admin
    create_default_admin()
    
    # Step 3: Create MongoDB indexes (optional)
    create_mongodb_indexes()
    
    print("\n" + "=" * 60)
    print("✅ Database setup complete!")
    print("=" * 60)
    
    print("\n📝 Next steps:")
    print("  1. Change admin password:")
    print("     Login with: admin / admin123")
    print("  2. Test the setup:")
    print("     pytest tests/test_database.py -v")
    print("  3. Start using LandGuard!")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Setup interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)