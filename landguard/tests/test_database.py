"""
Test database setup and connections.
"""

import pytest
from sqlalchemy.exc import OperationalError
from sqlalchemy import text
from pymongo.errors import ServerSelectionTimeoutError
import uuid

from database import (
    db_manager, User, LandRecord, AnalysisResult,
    AuditLog, RiskLevel, UserRole
)
from database.repositories import (
    UserRepository, LandRecordRepository,
    AnalysisResultRepository, AuditLogRepository
)


class TestDatabaseConnection:
    """Test database connection setup."""
    
    def test_postgresql_connection(self):
        """Test PostgreSQL connection."""
        try:
            engine = db_manager.get_pg_engine()
            with engine.connect() as conn:
                result = conn.execute(text("SELECT 1"))
                assert result.fetchone()[0] == 1
            print("✅ PostgreSQL connection successful")
        except OperationalError as e:
            pytest.skip(f"PostgreSQL not available: {e}")
    
    def test_mongodb_connection(self):
        """Test MongoDB connection."""
        try:
            mongo_db = db_manager.get_mongo_db()
            mongo_db.command('ping')
            print("✅ MongoDB connection successful")
        except ServerSelectionTimeoutError as e:
            pytest.skip(f"MongoDB not available: {e}")
    
    def test_create_tables(self):
        """Test table creation."""
        try:
            db_manager.create_pg_tables()
            print("✅ Tables created successfully")
        except Exception as e:
            pytest.fail(f"Failed to create tables: {e}")


class TestUserRepository:
    """Test User repository operations."""
    
    @pytest.fixture
    def session(self):
        """Create test database session."""
        session = db_manager.get_pg_session()
        yield session
        session.rollback()
        session.close()
    
    @pytest.fixture
    def user_repo(self, session):
        """Create user repository."""
        return UserRepository(session)
    
    def test_create_user(self, user_repo, session):
        """Test creating a user."""
        # Use unique identifiers to avoid conflicts
        unique_id = str(uuid.uuid4())[:8]
        user_data = {
            'username': f'test_analyst_{unique_id}',
            'email': f'analyst_{unique_id}@landguard.com',
            'hashed_password': 'hashed_password_here',
            'full_name': 'Test Analyst',
            'role': UserRole.ANALYST
        }
        
        user = user_repo.create(user_data)
        assert user.id is not None
        assert user.username == f'test_analyst_{unique_id}'
        assert user.role == UserRole.ANALYST
        print(f"✅ Created user: {user.username}")
        
        # Cleanup
        session.delete(user)
        session.commit()
    
    def test_get_user_by_username(self, user_repo, session):
        """Test retrieving user by username."""
        # Create user first with unique identifier
        unique_id = str(uuid.uuid4())[:8]
        user_data = {
            'username': f'test_user_{unique_id}',
            'email': f'test_{unique_id}@landguard.com',
            'hashed_password': 'hashed_password',
            'role': UserRole.VIEWER
        }
        created_user = user_repo.create(user_data)
        
        # Retrieve user
        retrieved_user = user_repo.get_by_username(f'test_user_{unique_id}')
        assert retrieved_user is not None
        assert retrieved_user.id == created_user.id
        print(f"✅ Retrieved user: {retrieved_user.username}")
        
        # Cleanup
        session.delete(created_user)
        session.commit()


class TestLandRecordRepository:
    """Test LandRecord repository operations."""
    
    @pytest.fixture
    def session(self):
        """Create test database session."""
        session = db_manager.get_pg_session()
        yield session
        session.rollback()
        session.close()
    
    @pytest.fixture
    def record_repo(self, session):
        """Create land record repository."""
        return LandRecordRepository(session)
    
    def test_create_land_record(self, record_repo, session):
        """Test creating a land record."""
        # Use unique land_id to avoid conflicts
        unique_id = str(uuid.uuid4())[:8]
        record_data = {
            'land_id': f'LND-TEST-{unique_id}',
            'location': 'Mumbai, Maharashtra',
            'area_sqft': 5000.0,
            'property_type': 'residential',
            'current_owner': 'Test Owner',
            'ownership_history': [],
            'transactions': [],
            'documents': []
        }
        
        record = record_repo.create(record_data)
        assert record.id is not None
        assert record.land_id == f'LND-TEST-{unique_id}'
        assert record.area_sqft == 5000.0
        print(f"✅ Created land record: {record.land_id}")
        
        # Cleanup
        session.delete(record)
        session.commit()
    
    def test_search_land_records(self, record_repo, session):
        """Test searching land records."""
        # Create test records with unique IDs
        unique_id = str(uuid.uuid4())[:8]
        record_data_1 = {
            'land_id': f'LND-SEARCH-{unique_id}-1',
            'location': 'Delhi, India',
            'area_sqft': 3000.0,
            'property_type': 'commercial',
            'current_owner': 'Owner A'
        }
        record_data_2 = {
            'land_id': f'LND-SEARCH-{unique_id}-2',
            'location': 'Delhi, India',
            'area_sqft': 4000.0,
            'property_type': 'residential',
            'current_owner': 'Owner B'
        }
        
        record_1 = record_repo.create(record_data_1)
        record_2 = record_repo.create(record_data_2)
        
        # Search by location
        results = record_repo.search(location='Delhi')
        assert len(results) >= 2
        print(f"✅ Found {len(results)} records in Delhi")
        
        # Cleanup
        session.delete(record_1)
        session.delete(record_2)
        session.commit()


class TestAnalysisResultRepository:
    """Test AnalysisResult repository operations."""
    
    @pytest.fixture
    def session(self):
        """Create test database session."""
        session = db_manager.get_pg_session()
        yield session
        session.rollback()
        session.close()
    
    @pytest.fixture
    def analysis_repo(self, session):
        """Create analysis result repository."""
        return AnalysisResultRepository(session)
    
    @pytest.fixture
    def land_record(self, session):
        """Create a test land record."""
        record_repo = LandRecordRepository(session)
        unique_id = str(uuid.uuid4())[:8]
        return record_repo.create({
            'land_id': f'LND-ANALYSIS-{unique_id}',
            'location': 'Test Location',
            'area_sqft': 2000.0,
            'property_type': 'residential',
            'current_owner': 'Test Owner'
        })
    
    def test_create_analysis(self, analysis_repo, land_record, session):
        """Test creating an analysis result."""
        analysis_data = {
            'land_record_id': land_record.id,
            'fraud_detected': True,
            'risk_score': 85.5,
            'risk_level': RiskLevel.HIGH,
            'confidence': 0.92,
            'fraud_indicators': {
                'rapid_ownership_changes': True,
                'price_anomaly': True,
                'shell_company_detected': False
            },
            'recommendations': 'Further investigation required',
            'model_version': '1.0.0',
            'ml_confidence': 0.89,
            'analysis_duration': 2.5
        }
        
        analysis = analysis_repo.create(analysis_data)
        assert analysis.id is not None
        assert analysis.fraud_detected is True
        assert analysis.risk_score == 85.5
        print(f"✅ Created analysis with risk score: {analysis.risk_score}")
        
        # Cleanup
        session.delete(analysis)
        session.delete(land_record)
        session.commit()


if __name__ == "__main__":
    print("🧪 Running database tests...\n")
    pytest.main([__file__, "-v", "--tb=short"])