"""Teste de integracao do endpoint /health: garante que a API responde 200
e que o payload confirma conectividade real com o banco (nao apenas que o
processo esta de pe)."""

import pytest
from httpx import ASGITransport, AsyncClient

from app.core.config import get_settings
from app.main import app


@pytest.mark.asyncio
async def test_health_returns_ok() -> None:
    settings = get_settings()
    transport = ASGITransport(app=app)

    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get(f"{settings.api_v1_prefix}/health")

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["database"] == "ok"
