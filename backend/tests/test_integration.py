# Integration tests
import pytest
from fastapi import status


@pytest.mark.integration
def test_full_user_flow(client):
    """Test complete user registration -> login -> access protected resource"""
    # 1. Register
    register_response = client.post(
       "/api/auth/register",
        json={
            "email": "integration@example.com",
            "password": "testpass123"
        }
    )
    assert register_response.status_code == status.HTTP_201_CREATED  # Registration returns 201
    token = register_response.json()["access_token"]
    
    # 2. Access protected resource
    headers = {"Authorization": f"Bearer {token}"}
    me_response = client.get("/api/auth/me", headers=headers)
    assert me_response.status_code == status.HTTP_200_OK
    assert me_response.json()["email"] == "integration@example.com"
    
    # 3. List PDFs (should be empty)
    pdf_response = client.get("/api/pdf/list", headers=headers)
    assert pdf_response.status_code == status.HTTP_200_OK
    assert pdf_response.json() == []


@pytest.mark.integration
def test_health_check(client):
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["status"] == "healthy"


@pytest.mark.integration
def test_root_endpoint(client):
    """Test root endpoint"""
    response = client.get("/")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["service"] == "Gradeup AI"
    assert "features" in data
