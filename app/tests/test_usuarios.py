"""Testes de aceite da Parte 3: hierarquia de criacao de usuarios,
aprovacao de auto-cadastro e isolamento multi-tenant (instituicao)."""

from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.usuario import Papel
from app.tests.conftest import criar_instituicao, criar_usuario


async def _token(client: AsyncClient, email: str, senha: str = "SenhaValida123") -> str:
    resp = await client.post("/api/v1/auth/login", json={"email": email, "senha": senha})
    assert resp.status_code == 200, resp.text
    return str(resp.json()["access_token"])


async def test_diretor_cria_coordenador(client: AsyncClient, db_session: AsyncSession) -> None:
    await criar_usuario(db_session, email="diretor1@teste.com", papel=Papel.DIRETOR)
    token = await _token(client, "diretor1@teste.com")

    resp = await client.post(
        "/api/v1/usuarios",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "nome": "Coordenador Novo",
            "email": "coord1@teste.com",
            "senha": "SenhaValida123",
            "papel": "coordenador",
        },
    )

    assert resp.status_code == 201, resp.text
    body = resp.json()
    assert body["papel"] == "coordenador"
    assert body["is_active"] is True  # criado por staff ja nasce ativo


async def test_diretor_pode_criar_papel_dois_niveis_abaixo(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    """Hierarquia e cumulativa (Diretor > Coordenador > Professor > Aluno):
    um Diretor pode criar um Professor diretamente, sem passar por um
    Coordenador intermediario."""
    await criar_usuario(db_session, email="diretor2@teste.com", papel=Papel.DIRETOR)
    token = await _token(client, "diretor2@teste.com")

    resp = await client.post(
        "/api/v1/usuarios",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "nome": "Professor Direto",
            "email": "prof.direto@teste.com",
            "senha": "SenhaValida123",
            "papel": "professor",
        },
    )
    assert resp.status_code == 201, resp.text


async def test_diretor_nao_cria_outro_diretor(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    await criar_usuario(db_session, email="diretor3@teste.com", papel=Papel.DIRETOR)
    token = await _token(client, "diretor3@teste.com")

    resp = await client.post(
        "/api/v1/usuarios",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "nome": "Outro Diretor",
            "email": "outrodiretor@teste.com",
            "senha": "SenhaValida123",
            "papel": "diretor",
        },
    )
    assert resp.status_code == 403


async def test_professor_nao_cria_outro_professor(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    """Criacao exige papel estritamente ABAIXO do criador - mesmo nivel
    tambem e proibido."""
    await criar_usuario(db_session, email="professor1@teste.com", papel=Papel.PROFESSOR)
    token = await _token(client, "professor1@teste.com")

    resp = await client.post(
        "/api/v1/usuarios",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "nome": "Outro Professor",
            "email": "outroprofessor@teste.com",
            "senha": "SenhaValida123",
            "papel": "professor",
        },
    )
    assert resp.status_code == 403


async def test_professor_cria_aluno(client: AsyncClient, db_session: AsyncSession) -> None:
    await criar_usuario(db_session, email="professor2@teste.com", papel=Papel.PROFESSOR)
    token = await _token(client, "professor2@teste.com")

    resp = await client.post(
        "/api/v1/usuarios",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "nome": "Aluno Cadastrado Pelo Professor",
            "email": "aluno.prof@teste.com",
            "senha": "SenhaValida123",
            "papel": "aluno",
        },
    )
    assert resp.status_code == 201
    assert resp.json()["is_active"] is True


async def test_aluno_nao_cria_ninguem(client: AsyncClient, db_session: AsyncSession) -> None:
    await criar_usuario(db_session, email="aluno.criador@teste.com", papel=Papel.ALUNO)
    token = await _token(client, "aluno.criador@teste.com")

    resp = await client.post(
        "/api/v1/usuarios",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "nome": "Ninguem",
            "email": "ninguem@teste.com",
            "senha": "SenhaValida123",
            "papel": "aluno",
        },
    )
    assert resp.status_code == 403


async def test_listagem_escopada_por_instituicao(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    inst_a = await criar_instituicao(db_session, nome="Escola A")
    inst_b = await criar_instituicao(db_session, nome="Escola B")
    await criar_usuario(
        db_session, email="diretorA@teste.com", papel=Papel.DIRETOR, instituicao_id=inst_a.id
    )
    await criar_usuario(
        db_session, email="diretorB@teste.com", papel=Papel.DIRETOR, instituicao_id=inst_b.id
    )
    await criar_usuario(
        db_session, email="professorA@teste.com", papel=Papel.PROFESSOR, instituicao_id=inst_a.id
    )

    token_a = await _token(client, "diretorA@teste.com")
    resp = await client.get("/api/v1/usuarios", headers={"Authorization": f"Bearer {token_a}"})

    assert resp.status_code == 200
    emails = {u["email"] for u in resp.json()}
    assert emails == {"diretora@teste.com", "professora@teste.com"}


async def test_aprovar_usuario_auto_cadastrado(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    instituicao = await criar_instituicao(db_session)
    await criar_usuario(
        db_session, email="professor.aprova@teste.com", papel=Papel.PROFESSOR,
        instituicao_id=instituicao.id,
    )

    registro = await client.post(
        "/api/v1/auth/register",
        json={
            "nome": "Pendente Aprovacao",
            "email": "pendente@teste.com",
            "senha": "SenhaValida123",
            "instituicao_codigo": instituicao.codigo,
            "aceite_lgpd": True,
        },
    )
    aluno_id = registro.json()["id"]

    login_antes = await client.post(
        "/api/v1/auth/login", json={"email": "pendente@teste.com", "senha": "SenhaValida123"}
    )
    assert login_antes.status_code == 403

    token_professor = await _token(client, "professor.aprova@teste.com")
    resp = await client.post(
        f"/api/v1/usuarios/{aluno_id}/aprovar",
        headers={"Authorization": f"Bearer {token_professor}"},
    )
    assert resp.status_code == 200
    assert resp.json()["is_active"] is True

    login_depois = await client.post(
        "/api/v1/auth/login", json={"email": "pendente@teste.com", "senha": "SenhaValida123"}
    )
    assert login_depois.status_code == 200


async def test_aprovar_usuario_de_outra_instituicao_falha(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    inst_a = await criar_instituicao(db_session)
    inst_b = await criar_instituicao(db_session)
    aluno = await criar_usuario(
        db_session, email="aluno.instB@teste.com", papel=Papel.ALUNO,
        instituicao_id=inst_b.id, is_active=False,
    )
    await criar_usuario(
        db_session, email="professor.instA@teste.com", papel=Papel.PROFESSOR,
        instituicao_id=inst_a.id,
    )

    token = await _token(client, "professor.instA@teste.com")
    resp = await client.post(
        f"/api/v1/usuarios/{aluno.id}/aprovar",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 403
