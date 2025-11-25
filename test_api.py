"""
Quick API testing script.
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_health():
    """Test health endpoint."""
    print("=" * 50)
    print("Testing Health Endpoint")
    print("=" * 50)
    
    response = requests.get(f"{BASE_URL}/api/v1/health")
    print(f"Status: {response.status_code}")
    print(json.dumps(response.json(), indent=2))
    print()

def test_auth():
    """Test authentication."""
    print("=" * 50)
    print("Testing Authentication")
    print("=" * 50)
    
    response = requests.post(
        f"{BASE_URL}/api/v1/auth/token",
        json={
            "username": "analyst_user",
            "password": "securepassword123"
        }
    )
    print(f"Status: {response.status_code}")
    data = response.json()
    print(json.dumps(data, indent=2))
    print()
    
    return data.get("access_token")

def test_analysis(token):
    """Test analysis endpoint."""
    print("=" * 50)
    print("Testing Analysis Endpoint")
    print("=" * 50)
    
    headers = {"Authorization": f"Bearer {token}"}
    
    data = {
        "land_id": "LAND-001",
        "owner_history": [
            {"owner_name": "John Doe", "date": "2020-01-15"},
            {"owner_name": "Jane Smith", "date": "2023-06-20"}
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
    
    response = requests.post(
        f"{BASE_URL}/api/v1/analyze",
        headers=headers,
        json=data
    )
    
    print(f"Status: {response.status_code}")
    print(json.dumps(response.json(), indent=2))
    print()

def test_batch_analysis(token):
    """Test batch analysis endpoint."""
    print("=" * 50)
    print("Testing Batch Analysis Endpoint")
    print("=" * 50)
    
    headers = {"Authorization": f"Bearer {token}"}
    
    data = {
        "records": [
            {
                "land_id": "LAND-001",
                "owner_history": [
                    {"owner_name": "John Doe", "date": "2020-01-15"},
                    {"owner_name": "Jane Smith", "date": "2023-06-20"}
                ],
                "transactions": [
                    {
                        "from_party": "John Doe",
                        "to_party": "Jane Smith",
                        "date": "2023-06-20",
                        "amount": 500000
                    }
                ]
            },
            {
                "land_id": "LAND-002",
                "owner_history": [
                    {"owner_name": "Alice Brown", "date": "2019-01-01"},
                    {"owner_name": "Bob White", "date": "2023-01-01"}
                ]
            }
        ]
    }
    
    response = requests.post(
        f"{BASE_URL}/api/v1/batch",
        headers=headers,
        json=data
    )
    
    print(f"Status: {response.status_code}")
    print(json.dumps(response.json(), indent=2))
    print()

def test_user_info(token):
    """Test user info endpoint."""
    print("=" * 50)
    print("Testing User Info Endpoint")
    print("=" * 50)
    
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(
        f"{BASE_URL}/api/v1/auth/me",
        headers=headers
    )
    
    print(f"Status: {response.status_code}")
    print(json.dumps(response.json(), indent=2))
    print()

if __name__ == "__main__":
    try:
        # Test endpoints
        test_health()
        token = test_auth()
        
        if token:
            test_user_info(token)
            test_analysis(token)
            test_batch_analysis(token)
        
        print("=" * 50)
        print("✅ All tests completed!")
        print("=" * 50)
        
    except Exception as e:
        print(f"❌ Error: {e}")