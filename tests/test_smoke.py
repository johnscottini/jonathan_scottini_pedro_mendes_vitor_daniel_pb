"""Teste básico de fumaça: garante que a aplicação sobe e responde."""

from core.config import API_VERSION


def test_health_esta_publico(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "version": API_VERSION}
