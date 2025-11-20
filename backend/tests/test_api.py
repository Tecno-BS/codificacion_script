"""
Tests básicos para la API
"""

import pytest
from fastapi.testclient import TestClient
from cod_backend.main import app

client = TestClient(app)


def test_root():
    """Test endpoint raíz"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "version" in data
    assert data["version"] == "0.6.0"


def test_health():
    """Test health check"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["service"] == "cod-backend"


def test_docs_available():
    """Test que la documentación está disponible"""
    response = client.get("/docs")
    assert response.status_code == 200

