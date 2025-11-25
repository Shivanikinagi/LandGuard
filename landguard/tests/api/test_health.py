"""
Tests for health check endpoints.
"""

import pytest
from fastapi.testclient import TestClient

from api.main import app

client = TestClient(app)


class TestHealthEndpoints:
    """Test health check endpoints."""
    
    def test_health_check(self):
        """Test health check endpoint."""
        response = client.get("/api/v1/health")
        
        assert response.status_code == 200
        
        data = response.json()
        assert data['status'] == 'healthy'
        assert 'version' in data
        assert 'timestamp' in data
        assert 'checks' in data
        assert data['checks']['api'] is True
    
    def test_ping(self):
        """Test ping endpoint."""
        response = client.get("/api/v1/ping")
        
        assert response.status_code == 200
        
        data = response.json()
        assert data['status'] == 'ok'
        assert 'timestamp' in data
    
    def test_root_endpoint(self):
        """Test root endpoint."""
        response = client.get("/")
        
        assert response.status_code == 200
        
        data = response.json()
        assert data['name'] == 'LandGuard API'
        assert 'version' in data
        assert data['status'] == 'operational'


if __name__ == "__main__":
    pytest.main([__file__, "-v"])