import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health_check():
    """Test the health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["status"] == "healthy"


def test_start_eligibility_assessment():
    """Test starting an eligibility assessment."""
    response = client.post("/assess-eligibility", json={})
    assert response.status_code == 200
    data = response.json()
    assert "session_id" in data
    assert data["progress"] == 0.0
    assert data["is_complete"] is False


def test_llm_provider_info():
    """Test getting LLM provider information."""
    response = client.get("/llm-provider-info")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "data" in data


def test_vector_store_stats():
    """Test getting vector store statistics."""
    response = client.get("/vector-store-stats")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True 