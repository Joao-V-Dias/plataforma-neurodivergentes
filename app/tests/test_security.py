"""Testes de seguranca basicos da Parte 8: acesso cross-role, tokens
expirados/adulterados/forjados, IDOR entre instituicoes (multi-tenant) e
tentativas de injecao via input. Nenhum destes cenarios deveria expor
stack trace, mensagem de erro do banco ou qualquer detalhe interno - toda
resposta de erro segue o envelope unico de app/schemas/error.py."""

from datetime import UTC, datetime, timedelta

import jwt
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.models.usuario import Papel
from app.tests.conftest import criar_instituicao, criar_turma, criar_usuario


async def _token(client: AsyncClient, email: str, senha: str = "SenhaValida123") -> str:
    resp = await client.post("/api/v1/auth/login", json={"email": email, "senha": senha})
    assert resp.status_code == 200, resp.text
    return str(resp.json()["access_token"])


def _auth(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def _forjar_token(
    *,
    usuario_id: str,
    papel: str = "diretor",
    tipo: str = "access",
    segredo: str | None = None,
    expira_em: timedelta = timedelta(minutes=15),
) -> str:
    """Monta um JWT manualmente, no mesmo formato de
    app/core/security.py:_encode - usado para simular tokens expirados,
    adulterados ou assinados com uma chave diferente da do servidor
    (forjados), cenarios que create_access_token() nao permite produzir
    de proposito."""
    settings = get_settings()
    agora = datetime.now(UTC)
    payload = {
        "sub": usuario_id,
        "papel": papel,
        "type": tipo,
        "jti": "11111111-1111-1111-1111-111111111111",
        "iat": agora,
        "exp": agora + expira_em,
    }
    return jwt.encode(payload, segredo or settings.secret_key, algorithm=settings.jwt_algorithm)


# --- Acesso cross-role -----------------------------------------------------


async def test_aluno_nao_acessa_endpoint_restrito_a_professor_mais(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    instituicao = await criar_instituicao(db_session)
    await criar_usuario(
        db_session, email="aluno.sec1@teste.com", papel=Papel.ALUNO,
        instituicao_id=instituicao.id,
    )
    token = await _token(client, "aluno.sec1@teste.com")

    resp_usuarios = await client.get("/api/v1/usuarios", headers=_auth(token))
    resp_turma = await client.post(
        "/api/v1/turmas",
        headers=_auth(token),
        json={"nome": "X", "periodo": "2026.1", "professor_responsavel_id": str(instituicao.id)},
    )
    resp_problema = await client.get("/api/v1/problemas", headers=_auth(token))

    assert resp_usuarios.status_code == 403
    assert resp_turma.status_code == 403
    assert resp_problema.status_code == 403
    for resp in (resp_usuarios, resp_turma, resp_problema):
        assert resp.json()["error"]["code"] == "http_error"


async def test_professor_nao_cria_usuario_de_papel_igual_ou_acima(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    """Hierarquia (app/services/usuario_service.py): Professor so cria
    Aluno - tentar criar Coordenador/Diretor/outro Professor e negado,
    mesmo autenticado e com payload valido."""
    instituicao = await criar_instituicao(db_session)
    await criar_usuario(
        db_session, email="prof.sec@teste.com", papel=Papel.PROFESSOR,
        instituicao_id=instituicao.id,
    )
    token = await _token(client, "prof.sec@teste.com")

    resp = await client.post(
        "/api/v1/usuarios",
        headers=_auth(token),
        json={
            "nome": "Tentativa Escalada",
            "email": "escalada@teste.com",
            "senha": "SenhaValida123",
            "papel": "diretor",
        },
    )
    assert resp.status_code == 403


async def test_sem_token_endpoint_protegido_devolve_401(client: AsyncClient) -> None:
    resp = await client.get("/api/v1/usuarios")
    assert resp.status_code == 401


# --- Tokens expirados / adulterados / forjados ------------------------------


async def test_token_expirado_e_rejeitado(client: AsyncClient, db_session: AsyncSession) -> None:
    instituicao = await criar_instituicao(db_session)
    usuario = await criar_usuario(
        db_session, email="aluno.expirado@teste.com", papel=Papel.ALUNO,
        instituicao_id=instituicao.id,
    )
    token_expirado = _forjar_token(
        usuario_id=str(usuario.id), papel="aluno", expira_em=timedelta(minutes=-5)
    )

    resp = await client.get("/api/v1/auth/me", headers=_auth(token_expirado))
    assert resp.status_code == 401


async def test_token_com_assinatura_adulterada_e_rejeitado(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    instituicao = await criar_instituicao(db_session)
    await criar_usuario(
        db_session, email="aluno.adulterado@teste.com", papel=Papel.ALUNO,
        instituicao_id=instituicao.id,
    )
    token_valido = await _token(client, "aluno.adulterado@teste.com")
    # Troca um caractere no MEIO da assinatura (nao o ultimo): a base64url
    # de uma assinatura HMAC-SHA256 tem um resto de bits sem significado
    # no ultimo caractere (padding implicito), entao alterar exatamente o
    # ultimo caractere ocasionalmente decodifica para os mesmos bytes -
    # flakiness real que ja apareceu aqui. No meio da string isso nao
    # acontece: qualquer troca ali muda um byte decodificado de verdade.
    meio = len(token_valido) // 2
    caractere_trocado = "A" if token_valido[meio] != "A" else "B"
    token_adulterado = token_valido[:meio] + caractere_trocado + token_valido[meio + 1 :]

    resp = await client.get("/api/v1/auth/me", headers=_auth(token_adulterado))
    assert resp.status_code == 401


async def test_token_forjado_com_segredo_diferente_e_rejeitado(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    """Simula um atacante que nao conhece o SECRET_KEY do servidor
    tentando forjar um token de Diretor para uma instituicao arbitraria."""
    instituicao = await criar_instituicao(db_session)
    usuario = await criar_usuario(
        db_session, email="aluno.forjado@teste.com", papel=Papel.ALUNO,
        instituicao_id=instituicao.id,
    )
    token_forjado = _forjar_token(
        usuario_id=str(usuario.id), papel="diretor", segredo="chave-que-o-atacante-inventou"
    )

    resp = await client.get("/api/v1/auth/me", headers=_auth(token_forjado))
    assert resp.status_code == 401


async def test_token_de_refresh_nao_e_aceito_como_access(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    """decode_token valida o campo `type` do payload - um refresh token
    nao pode ser reaproveitado para autenticar chamadas normais."""
    instituicao = await criar_instituicao(db_session)
    usuario = await criar_usuario(
        db_session, email="aluno.tipoerrado@teste.com", papel=Papel.ALUNO,
        instituicao_id=instituicao.id,
    )
    token_refresh = _forjar_token(usuario_id=str(usuario.id), papel="aluno", tipo="refresh")

    resp = await client.get("/api/v1/auth/me", headers=_auth(token_refresh))
    assert resp.status_code == 401


async def test_papel_no_token_forjado_nao_sobrescreve_o_papel_real_no_banco(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    """Mesmo que um token (forjado com o SECRET_KEY certo, cenario
    hipotetico de vazamento de chave) declare papel=diretor, o backend
    resolve o usuario pelo `sub` e usa o papel gravado no banco
    (app/api/deps.py:get_current_user) - nunca confia no claim do token
    para autorizacao alem da propria identidade."""
    instituicao = await criar_instituicao(db_session)
    aluno = await criar_usuario(
        db_session, email="aluno.claimfalso@teste.com", papel=Papel.ALUNO,
        instituicao_id=instituicao.id,
    )
    token_com_papel_falso = _forjar_token(usuario_id=str(aluno.id), papel="diretor")

    resp_me = await client.get("/api/v1/auth/me", headers=_auth(token_com_papel_falso))
    assert resp_me.status_code == 200
    assert resp_me.json()["papel"] == "aluno"

    resp_usuarios = await client.get(
        "/api/v1/usuarios", headers=_auth(token_com_papel_falso)
    )
    assert resp_usuarios.status_code == 403


# --- IDOR / isolamento multi-tenant -----------------------------------------


async def test_professor_de_outra_instituicao_nao_acessa_turma(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    instituicao_a = await criar_instituicao(db_session)
    professor_a = await criar_usuario(
        db_session, email="prof.instA@teste.com", papel=Papel.PROFESSOR,
        instituicao_id=instituicao_a.id,
    )
    turma_a = await criar_turma(
        db_session, instituicao_id=instituicao_a.id, professor_responsavel_id=professor_a.id
    )

    instituicao_b = await criar_instituicao(db_session)
    await criar_usuario(
        db_session, email="prof.instB@teste.com", papel=Papel.PROFESSOR,
        instituicao_id=instituicao_b.id,
    )
    token_b = await _token(client, "prof.instB@teste.com")

    resp = await client.get(f"/api/v1/turmas/{turma_a.id}", headers=_auth(token_b))
    # 404, nao 403: o backend nao revela que o recurso existe em outra
    # instituicao (ver app/api/deps.py:get_turma_acessivel).
    assert resp.status_code == 404


async def test_aluno_de_outra_instituicao_nao_ve_perfil_de_aluno_alheio(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    instituicao_a = await criar_instituicao(db_session)
    aluno_a = await criar_usuario(
        db_session, email="aluno.instA@teste.com", papel=Papel.ALUNO,
        instituicao_id=instituicao_a.id,
    )

    instituicao_b = await criar_instituicao(db_session)
    await criar_usuario(
        db_session, email="aluno.instB@teste.com", papel=Papel.ALUNO,
        instituicao_id=instituicao_b.id,
    )
    token_b = await _token(client, "aluno.instB@teste.com")

    resp = await client.get(f"/api/v1/alunos/{aluno_a.id}/perfil", headers=_auth(token_b))
    assert resp.status_code == 403


# --- Tentativas de injecao ---------------------------------------------------


@pytest.mark.parametrize(
    "carga",
    [
        "' OR '1'='1",
        "'; DROP TABLE usuarios; --",
        "admin@teste.com' --",
    ],
)
async def test_login_com_payload_de_injecao_no_email_e_apenas_rejeitado(
    client: AsyncClient, carga: str
) -> None:
    """`email` e validado como EmailStr pelo Pydantic antes de qualquer
    consulta ao banco - uma carga de SQL injection nem chega a virar
    query, so falha validacao de formato (422). O ORM (SQLAlchemy, com
    bind parameters) tambem impediria a injecao mesmo se o formato
    passasse, mas a validacao de schema e a primeira barreira."""
    resp = await client.post(
        "/api/v1/auth/login", json={"email": carga, "senha": "qualquercoisa123"}
    )
    assert resp.status_code == 422
    assert resp.json()["error"]["code"] == "validation_error"


async def test_nome_com_caracteres_de_injecao_e_armazenado_como_texto_literal(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    """Campos de texto livre (nome) aceitam qualquer caractere - a
    seguranca vem do ORM parametrizar a query, nao de filtrar input. O
    valor deve ir e voltar exatamente como enviado, sem quebrar a
    aplicacao nem executar nada."""
    instituicao = await criar_instituicao(db_session)
    await criar_usuario(
        db_session, email="diretor.sec@teste.com", papel=Papel.DIRETOR,
        instituicao_id=instituicao.id,
    )
    token = await _token(client, "diretor.sec@teste.com")

    nome_malicioso = "Robert'); DROP TABLE usuarios;--"
    resp = await client.post(
        "/api/v1/usuarios",
        headers=_auth(token),
        json={
            "nome": nome_malicioso,
            "email": "bobby.tables@teste.com",
            "senha": "SenhaValida123",
            "papel": "aluno",
        },
    )
    assert resp.status_code == 201
    assert resp.json()["nome"] == nome_malicioso

    # A tabela usuarios sobreviveu - uma nova consulta funciona normalmente.
    resp_listagem = await client.get("/api/v1/usuarios", headers=_auth(token))
    assert resp_listagem.status_code == 200
    assert any(u["email"] == "bobby.tables@teste.com" for u in resp_listagem.json())


# --- Erros nunca vazam detalhe interno ---------------------------------------


async def test_erro_de_validacao_nunca_expoe_stack_trace_ou_tipo_python(
    client: AsyncClient,
) -> None:
    resp = await client.post("/api/v1/auth/login", json={"email": "nao-e-email"})
    body = resp.json()
    texto_completo = str(body)
    assert "Traceback" not in texto_completo
    assert "pydantic" not in texto_completo.lower()
    assert set(body.keys()) == {"error", "request_id"}
