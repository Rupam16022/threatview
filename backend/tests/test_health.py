from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_root_endpoint():
    """Verify the root endpoint returns service info."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "ThreatView"
    assert "documentation" in data
    assert "health" in data


def test_health_check_endpoint():
    """Verify the /api/health endpoint returns healthy status and metadata."""
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "ThreatView"
    assert data["version"] == "0.1.0"
    assert "timestamp" in data
