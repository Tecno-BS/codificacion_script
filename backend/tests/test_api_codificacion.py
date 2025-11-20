"""
Tests para rutas de codificación de la API
"""
import pytest
from fastapi.testclient import TestClient
from cod_backend.main import app

client = TestClient(app)


def test_health_endpoint():
    """Test del endpoint de health con modelo actualizado"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["version"] == "0.8.0"
    assert "modo_mock" in data
    assert "openai_disponible" in data


def test_listar_modelos():
    """Test listar modelos GPT disponibles"""
    response = client.get("/api/v1/modelos")
    assert response.status_code == 200
    data = response.json()
    assert "modelos" in data
    assert len(data["modelos"]) > 0
    assert any(m["id"] == "gpt-4o-mini" for m in data["modelos"])


@pytest.mark.skip(reason="Requiere archivos de prueba reales")
def test_codificar_respuestas():
    """
    Test de codificación completa (skip por defecto)
    Requiere archivos de prueba reales
    """
    response = client.post(
        "/api/v1/codificar",
        json={
            "ruta_respuestas": "data/test_respuestas.xlsx",
            "ruta_codigos": "data/test_codigos.xlsx",
            "modelo": "gpt-4o-mini"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "mensaje" in data
    assert "total_respuestas" in data
    assert "costo_total" in data


def test_codificar_archivo_inexistente():
    """Test con archivo que no existe"""
    response = client.post(
        "/api/v1/codificar",
        json={
            "ruta_respuestas": "archivo_que_no_existe.xlsx",
            "modelo": "gpt-4o-mini"
        }
    )
    # Puede ser 404 o 500 dependiendo de cómo el codificador maneja el error
    assert response.status_code in [404, 500]
    if response.status_code == 404:
        assert "no encontrado" in response.json()["detail"].lower()
    else:
        # Error 500 con mensaje de error
        assert "detail" in response.json() or "message" in response.json()


def test_root_endpoint():
    """Test del endpoint raíz"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "nombre" in data or "message" in data
    assert "version" in data
    assert data["version"] == "0.8.0"

