"""
Tests for authentication endpoints.
"""

import pytest
from fastapi.testclient import TestClient

from api.main import app

client = TestClient(app)


class TestAuthEndpoints:
    """Test authentication endpoints."""
    
    def test_create_token_success(self):
        """Test successful token creation."""
        response = client.post(
            "/api/v1/auth/token",
            json={
                "username": "analyst_user",
                "password": "securepassword123"
            }
        )
        
        assert response.status_code == 200
        
        data = response.json()
        assert 'access_token' in data
        assert data['token_type'] == 'bearer'
        assert data['expires_in'] == 86400
    
    def test_create_token_short_password(self):
        """Test token creation with short password (Pydantic validation)."""
        response = client.post(
            "/api/v1/auth/token",
            json={
                "username": "test_user",
                "password": "short"
            }
        )
        
        # Pydantic returns 422 for validation errors
        assert response.status_code == 422
    
    def test_create_token_admin_role(self):
        """Test token creation for admin user."""
        response = client.post(
            "/api/v1/auth/token",
            json={
                "username": "admin_user",
                "password": "securepassword123"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert 'access_token' in data
    
    def test_get_user_info_without_auth(self):
        """Test getting user info without authentication."""
        response = client.get("/api/v1/auth/me")
        
        assert response.status_code == 401
    
    def test_get_user_info_with_token(self):
        """Test getting user info with valid token."""
        # First get a token
        token_response = client.post(
            "/api/v1/auth/token",
            json={
                "username": "analyst_user",
                "password": "securepassword123"
            }
        )
        
        token = token_response.json()['access_token']
        
        # Now get user info
        response = client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        
        data = response.json()
        assert 'user_id' in data
        assert 'role' in data
        assert 'permissions' in data
    
    def test_create_api_key_without_admin(self):
        """Test creating API key without admin role."""
        # Get analyst token
        token_response = client.post(
            "/api/v1/auth/token",
            json={
                "username": "analyst_user",
                "password": "securepassword123"
            }
        )
        
        token = token_response.json()['access_token']
        
        # Try to create API key
        response = client.post(
            "/api/v1/auth/api-key/create?role=viewer",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 403


if __name__ == "__main__":
    pytest.main([__file__, "-v"])