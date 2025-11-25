"""
Tests for analysis endpoints.
"""

import pytest
from fastapi.testclient import TestClient

from api.main import app

client = TestClient(app)


@pytest.fixture
def analyst_token():
    """Get analyst token for testing."""
    response = client.post(
        "/api/v1/auth/token",
        json={
            "username": "analyst_user",
            "password": "securepassword123"
        }
    )
    return response.json()['access_token']


@pytest.fixture
def viewer_token():
    """Get viewer token for testing."""
    response = client.post(
        "/api/v1/auth/token",
        json={
            "username": "viewer_user",
            "password": "securepassword123"
        }
    )
    return response.json()['access_token']


@pytest.fixture
def sample_land_record():
    """Sample land record for testing."""
    return {
        "land_id": "LAND-TEST-001",
        "owner_history": [
            {
                "owner_name": "John Doe",
                "date": "2020-01-15"
            },
            {
                "owner_name": "Jane Smith",
                "date": "2023-06-20"
            }
        ],
        "transactions": [
            {
                "from_party": "John Doe",
                "to_party": "Jane Smith",
                "date": "2023-06-20",
                "amount": 500000
            }
        ]
    }


class TestAnalysisEndpoints:
    """Test analysis endpoints."""
    
    def test_analyze_without_auth(self, sample_land_record):
        """Test analysis without authentication."""
        response = client.post(
            "/api/v1/analyze",
            json=sample_land_record
        )
        
        assert response.status_code == 401
    
    def test_analyze_with_viewer_role(self, viewer_token, sample_land_record):
        """Test analysis with viewer role (should fail)."""
        response = client.post(
            "/api/v1/analyze",
            json=sample_land_record,
            headers={"Authorization": f"Bearer {viewer_token}"}
        )
        
        assert response.status_code == 403
    
    def test_analyze_with_analyst_role(self, analyst_token, sample_land_record):
        """Test successful analysis with analyst role."""
        response = client.post(
            "/api/v1/analyze",
            json=sample_land_record,
            headers={"Authorization": f"Bearer {analyst_token}"}
        )
        
        assert response.status_code == 200
        
        data = response.json()
        assert 'land_id' in data
        assert data['land_id'] == sample_land_record['land_id']
        assert 'fraud_detected' in data
        assert 'risk_score' in data
        assert 'fraud_indicators' in data
        assert 'analysis_timestamp' in data
    
    def test_analyze_invalid_land_id(self, analyst_token):
        """Test analysis with invalid land ID."""
        invalid_record = {
            "land_id": "<script>alert('xss')</script>",
            "owner_history": [
                {
                    "owner_name": "Test User",
                    "date": "2020-01-01"
                }
            ]
        }
        
        response = client.post(
            "/api/v1/analyze",
            json=invalid_record,
            headers={"Authorization": f"Bearer {analyst_token}"}
        )
        
        assert response.status_code == 400
    
    def test_batch_analyze(self, analyst_token, sample_land_record):
        """Test batch analysis."""
        batch_request = {
            "records": [
                sample_land_record,
                {
                    "land_id": "LAND-TEST-002",
                    "owner_history": [
                        {
                            "owner_name": "Alice",
                            "date": "2019-01-01"
                        }
                    ]
                }
            ]
        }
        
        response = client.post(
            "/api/v1/batch",
            json=batch_request,
            headers={"Authorization": f"Bearer {analyst_token}"}
        )
        
        assert response.status_code == 200
        
        data = response.json()
        assert data['total_records'] == 2
        assert data['records_analyzed'] == 2
        assert 'results' in data
        assert len(data['results']) == 2
        assert 'batch_id' in data
        assert 'processing_time_seconds' in data
    
    def test_batch_analyze_too_many_records(self, analyst_token, sample_land_record):
        """Test batch analysis with too many records (Pydantic validation)."""
        batch_request = {
            "records": [sample_land_record] * 101
        }
        
        response = client.post(
            "/api/v1/batch",
            json=batch_request,
            headers={"Authorization": f"Bearer {analyst_token}"}
        )
        
        # Pydantic returns 422 for validation errors
        assert response.status_code == 422


if __name__ == "__main__":
    pytest.main([__file__, "-v"])