"""Testes de aceite da Parte 2: login, RBAC, rotacao de refresh token,
recuperacao de senha e protecao de dados sensiveis (senha nunca em texto
puro, nunca vazada em respostas de erro)."""

import uuid
from datetime import UTC, datetime, timedelta

import jwt
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.models.usuario import Papel
from app.tests.conftest import criar_usuario


def _token_expirado(usuario_id: uuid.UUID, papel: Papel) -> str:
    settings = get_settings()
    payload = {
        "sub": str(usuario_id),
        "papel": papel.value,
        "type": "access",
        "jti": str(uuid.uuid4()),
        "iat": datetime.now(UTC) - timedelta(minutes=30),
        "exp": datetime.now(UTC) - timedelta(minutes=1),
    }
    return jwt.encode(payload, settings.secret_key, algorithm=settings.jwt_algorithm)


async def test_login_sucesso(client: AsyncClient, db_session: AsyncSession) -> None:
    await criar_usuario(db_session, email="login.ok@teste.com", senha="SenhaValida123")

    resp = await client.post(
        "/api/v1/auth/login", json={"email": "login.ok@teste.com", "senha": "SenhaValida123"}
    )

    assert resp.status_code == 200
    body = resp.json()
    assert "access_token" in body
    assert "refresh_token" in body
    assert body["token_type"] == "bearer"


async def test_login_credenciais_invalidas(client: AsyncClient, db_session: AsyncSession) -> None:
    await criar_usuario(db_session, email="login.errado@teste.com", senha="SenhaValida123")

    resp = await client.post(
        "/api/v1/auth/login", json={"email": "login.errado@teste.com", "senha": "senha_errada"}
    )

    assert resp.status_code == 401


async def test_senha_nunca_armazenada_em_texto_puro(db_session: AsyncSession) -> None:
    usuario = await criar_usuario(db_session, email="hash.teste@teste.com", senha="SenhaValida123")

    assert usuario.senha_hash != "SenhaValida123"
    assert usuario.senha_hash.startswith("$argon2")


async def test_erro_de_validacao_nao_vaza_senha_submetida(client: AsyncClient) -> None:
    segredo = "SenhaSecretaXPTO"
    resp = await client.post(
        "/api/v1/auth/register",
        json={
            "nome": "Teste",
            "email": "vaza@teste.com",
            "senha": segredo[:3],  # forca erro de validacao (menor que 8 chars)
            "aceite_lgpd": True,
        },
    )

    assert resp.status_code == 422
    assert segredo not in resp.text
    assert segredo[:3] not in resp.text


async def test_rota_protegida_exige_token(client: AsyncClient) -> None:
    resp = await client.get("/api/v1/auth/me")
    assert resp.status_code == 401


async def test_rota_protegida_rejeita_token_invalido(client: AsyncClient) -> None:
    resp = await client.get(
        "/api/v1/auth/me", headers={"Authorization": "Bearer token.completamente.invalido"}
    )
    assert resp.status_code == 401


async def test_rota_protegida_rejeita_token_expirado(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    usuario = await criar_usuario(db_session, email="expirado@teste.com")
    token = _token_expirado(usuario.id, usuario.papel)

    resp = await client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 401


async def test_aluno_nao_acessa_rota_de_professor(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    await criar_usuario(
        db_session, email="aluno.rbac@teste.com", senha="SenhaValida123", papel=Papel.ALUNO
    )
    login = await client.post(
        "/api/v1/auth/login", json={"email": "aluno.rbac@teste.com", "senha": "SenhaValida123"}
    )
    token = login.json()["access_token"]

    resp = await client.get("/api/v1/usuarios", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 403


async def test_professor_acessa_rota_de_professor(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    await criar_usuario(
        db_session,
        email="professor.rbac@teste.com",
        senha="SenhaValida123",
        papel=Papel.PROFESSOR,
    )
    login = await client.post(
        "/api/v1/auth/login",
        json={"email": "professor.rbac@teste.com", "senha": "SenhaValida123"},
    )
    token = login.json()["access_token"]

    resp = await client.get("/api/v1/usuarios", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200


async def test_refresh_rotaciona_e_detecta_reuso(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    await criar_usuario(db_session, email="refresh@teste.com", senha="SenhaValida123")
    login = await client.post(
        "/api/v1/auth/login", json={"email": "refresh@teste.com", "senha": "SenhaValida123"}
    )
    refresh_token_original = login.json()["refresh_token"]

    primeiro_refresh = await client.post(
        "/api/v1/auth/refresh", json={"refresh_token": refresh_token_original}
    )
    assert primeiro_refresh.status_code == 200
    novo_refresh_token = primeiro_refresh.json()["refresh_token"]

    # Reusar o refresh token original (ja rotacionado) deve falhar...
    reuso = await client.post(
        "/api/v1/auth/refresh", json={"refresh_token": refresh_token_original}
    )
    assert reuso.status_code == 401

    # ...e, por seguranca, revoga tambem o token novo emitido na rotacao.
    tentativa_com_novo = await client.post(
        "/api/v1/auth/refresh", json={"refresh_token": novo_refresh_token}
    )
    assert tentativa_com_novo.status_code == 401


async def test_logout_revoga_refresh_token(client: AsyncClient, db_session: AsyncSession) -> None:
    await criar_usuario(db_session, email="logout@teste.com", senha="SenhaValida123")
    login = await client.post(
        "/api/v1/auth/login", json={"email": "logout@teste.com", "senha": "SenhaValida123"}
    )
    refresh_token = login.json()["refresh_token"]

    logout_resp = await client.post("/api/v1/auth/logout", json={"refresh_token": refresh_token})
    assert logout_resp.status_code == 204

    resp = await client.post("/api/v1/auth/refresh", json={"refresh_token": refresh_token})
    assert resp.status_code == 401


async def test_registro_aluno_exige_consentimento_lgpd(client: AsyncClient) -> None:
    resp = await client.post(
        "/api/v1/auth/register",
        json={
            "nome": "Sem Consentimento",
            "email": "semconsentimento@teste.com",
            "senha": "SenhaValida123",
            "aceite_lgpd": False,
        },
    )
    assert resp.status_code == 400


async def test_registro_aluno_email_duplicado(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    await criar_usuario(db_session, email="duplicado@teste.com")

    resp = await client.post(
        "/api/v1/auth/register",
        json={
            "nome": "Duplicado",
            "email": "duplicado@teste.com",
            "senha": "SenhaValida123",
            "aceite_lgpd": True,
        },
    )
    assert resp.status_code == 409


async def test_conta_inativa_nao_faz_login(client: AsyncClient, db_session: AsyncSession) -> None:
    await criar_usuario(
        db_session, email="inativo@teste.com", senha="SenhaValida123", is_active=False
    )

    resp = await client.post(
        "/api/v1/auth/login", json={"email": "inativo@teste.com", "senha": "SenhaValida123"}
    )
    assert resp.status_code == 403


async def test_forgot_password_nao_revela_existencia_do_email(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    await criar_usuario(db_session, email="existente@teste.com", senha="SenhaValida123")

    resp_existente = await client.post(
        "/api/v1/auth/forgot-password", json={"email": "existente@teste.com"}
    )
    resp_inexistente = await client.post(
        "/api/v1/auth/forgot-password", json={"email": "nao.existe@teste.com"}
    )

    assert resp_existente.status_code == resp_inexistente.status_code == 200
    assert resp_existente.json()["message"] == resp_inexistente.json()["message"]
    assert resp_existente.json()["reset_token"] is not None
    assert resp_inexistente.json()["reset_token"] is None


async def test_reset_password_token_uso_unico(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    await criar_usuario(db_session, email="reset@teste.com", senha="SenhaAntiga123")

    forgot = await client.post("/api/v1/auth/forgot-password", json={"email": "reset@teste.com"})
    token = forgot.json()["reset_token"]
    assert token is not None

    primeiro_uso = await client.post(
        "/api/v1/auth/reset-password", json={"token": token, "nova_senha": "SenhaNova456"}
    )
    assert primeiro_uso.status_code == 204

    login_com_senha_nova = await client.post(
        "/api/v1/auth/login", json={"email": "reset@teste.com", "senha": "SenhaNova456"}
    )
    assert login_com_senha_nova.status_code == 200

    segundo_uso = await client.post(
        "/api/v1/auth/reset-password", json={"token": token, "nova_senha": "OutraSenha789"}
    )
    assert segundo_uso.status_code == 400


async def test_rate_limit_login_bloqueia_apos_limite(client: AsyncClient) -> None:
    settings = get_settings()
    limite = int(settings.rate_limit_login.split("/")[0])

    respostas = []
    for _ in range(limite + 2):
        resp = await client.post(
            "/api/v1/auth/login", json={"email": "rate.limit@teste.com", "senha": "errada"}
        )
        respostas.append(resp.status_code)

    assert 429 in respostas
