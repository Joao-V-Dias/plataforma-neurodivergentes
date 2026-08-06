"""Testes de aceite da Parte 3: perfil de neurodivergencia (versionado),
questionario Big Five (TIPI) e preferencias de acessibilidade - incluindo
que dados sensiveis tem acesso restrito por papel/instituicao."""

from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.usuario import Papel
from app.services.big_five_service import calcular_scores
from app.tests.conftest import criar_instituicao, criar_usuario


async def _token(client: AsyncClient, email: str, senha: str = "SenhaValida123") -> str:
    resp = await client.post("/api/v1/auth/login", json={"email": email, "senha": senha})
    assert resp.status_code == 200, resp.text
    return str(resp.json()["access_token"])


def _auth(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


async def test_aluno_registra_e_confere_proprio_perfil(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    aluno = await criar_usuario(db_session, email="aluno.perfil@teste.com", papel=Papel.ALUNO)
    token = await _token(client, "aluno.perfil@teste.com")

    resp = await client.post(
        f"/api/v1/alunos/{aluno.id}/perfil",
        headers=_auth(token),
        json={
            "condicoes_codigos": ["tdah"],
            "observacoes": "Laudo anexado.",
            "aceite_consentimento": True,
        },
    )
    assert resp.status_code == 201, resp.text
    body = resp.json()
    assert body["versao"] == 1
    assert {c["codigo"] for c in body["condicoes"]} == {"tdah"}

    vigente = await client.get(f"/api/v1/alunos/{aluno.id}/perfil", headers=_auth(token))
    assert vigente.status_code == 200
    assert vigente.json()["versao"] == 1


async def test_perfil_exige_consentimento_especifico(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    aluno = await criar_usuario(db_session, email="aluno.semconsent@teste.com", papel=Papel.ALUNO)
    token = await _token(client, "aluno.semconsent@teste.com")

    resp = await client.post(
        f"/api/v1/alunos/{aluno.id}/perfil",
        headers=_auth(token),
        json={"condicoes_codigos": [], "aceite_consentimento": False},
    )
    assert resp.status_code == 400


async def test_perfil_codigo_condicao_invalido(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    aluno = await criar_usuario(db_session, email="aluno.codigoinv@teste.com", papel=Papel.ALUNO)
    token = await _token(client, "aluno.codigoinv@teste.com")

    resp = await client.post(
        f"/api/v1/alunos/{aluno.id}/perfil",
        headers=_auth(token),
        json={"condicoes_codigos": ["codigo-que-nao-existe"], "aceite_consentimento": True},
    )
    assert resp.status_code == 422


async def test_perfil_versiona_sem_sobrescrever_historico(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    aluno = await criar_usuario(db_session, email="aluno.versao@teste.com", papel=Papel.ALUNO)
    token = await _token(client, "aluno.versao@teste.com")

    await client.post(
        f"/api/v1/alunos/{aluno.id}/perfil",
        headers=_auth(token),
        json={"condicoes_codigos": ["tdah"], "aceite_consentimento": True},
    )
    await client.post(
        f"/api/v1/alunos/{aluno.id}/perfil",
        headers=_auth(token),
        json={"condicoes_codigos": ["tdah", "dislexia"], "aceite_consentimento": True},
    )

    vigente = await client.get(f"/api/v1/alunos/{aluno.id}/perfil", headers=_auth(token))
    assert vigente.json()["versao"] == 2
    assert {c["codigo"] for c in vigente.json()["condicoes"]} == {"tdah", "dislexia"}

    historico = await client.get(
        f"/api/v1/alunos/{aluno.id}/perfil/historico", headers=_auth(token)
    )
    versoes = [v["versao"] for v in historico.json()]
    assert versoes == [2, 1]  # historico completo preservado, mais recente primeiro
    assert {c["codigo"] for c in historico.json()[1]["condicoes"]} == {"tdah"}  # v1 intacta


async def test_professor_acessa_perfil_de_aluno_da_mesma_instituicao(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    instituicao = await criar_instituicao(db_session)
    aluno = await criar_usuario(
        db_session, email="aluno.prof.perfil@teste.com", papel=Papel.ALUNO,
        instituicao_id=instituicao.id,
    )
    await criar_usuario(
        db_session, email="professor.perfil@teste.com", papel=Papel.PROFESSOR,
        instituicao_id=instituicao.id,
    )
    token_professor = await _token(client, "professor.perfil@teste.com")

    resp = await client.post(
        f"/api/v1/alunos/{aluno.id}/perfil",
        headers=_auth(token_professor),
        json={"condicoes_codigos": ["tea"], "aceite_consentimento": True},
    )
    assert resp.status_code == 201
    assert resp.json()["criado_por_id"] != str(aluno.id)


async def test_professor_de_outra_instituicao_nao_acessa_perfil(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    inst_a = await criar_instituicao(db_session)
    inst_b = await criar_instituicao(db_session)
    aluno = await criar_usuario(
        db_session, email="aluno.instA@teste.com", papel=Papel.ALUNO, instituicao_id=inst_a.id
    )
    await criar_usuario(
        db_session, email="professor.instB@teste.com", papel=Papel.PROFESSOR,
        instituicao_id=inst_b.id,
    )
    token = await _token(client, "professor.instB@teste.com")

    resp = await client.get(f"/api/v1/alunos/{aluno.id}/perfil", headers=_auth(token))
    assert resp.status_code == 403


async def test_aluno_nao_acessa_perfil_de_outro_aluno(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    instituicao = await criar_instituicao(db_session)
    aluno_alvo = await criar_usuario(
        db_session, email="aluno.alvo@teste.com", papel=Papel.ALUNO, instituicao_id=instituicao.id
    )
    await criar_usuario(
        db_session, email="aluno.curioso@teste.com", papel=Papel.ALUNO,
        instituicao_id=instituicao.id,
    )
    token = await _token(client, "aluno.curioso@teste.com")

    resp = await client.get(f"/api/v1/alunos/{aluno_alvo.id}/perfil", headers=_auth(token))
    assert resp.status_code == 403


def test_calculo_tipi_e_fiel_a_formula_publicada() -> None:
    # Respostas nos itens impares (1,3,5,7,9) = 7; pares (2,4,6,8,10) = 1.
    # Todo item par e reverso, exceto o item 4 ("ansioso", direto). Como o
    # item 4 = 1 (discordo de "ansioso") e o item 9 = 7 (concordo com
    # "calmo", reverso -> vira 8-7=1), Neuroticismo fica baixo (1.0),
    # diferente das outras 4 dimensoes (todas altas, 7.0).
    scores = calcular_scores([7, 1, 7, 1, 7, 1, 7, 1, 7, 1])
    assert scores == {
        "extroversao": 7.0,
        "amabilidade": 7.0,
        "conscienciosidade": 7.0,
        "neuroticismo": 1.0,
        "abertura": 7.0,
    }

    neutro = calcular_scores([4] * 10)
    assert all(v == 4.0 for v in neutro.values())


async def test_aluno_responde_big_five_via_api(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    await criar_usuario(db_session, email="aluno.bigfive@teste.com", papel=Papel.ALUNO)
    token = await _token(client, "aluno.bigfive@teste.com")

    questionario = await client.get("/api/v1/big-five/questionario", headers=_auth(token))
    assert questionario.status_code == 200
    assert len(questionario.json()) == 10

    resp = await client.post(
        "/api/v1/me/big-five",
        headers=_auth(token),
        json={"respostas": [7, 1, 7, 1, 7, 1, 7, 1, 7, 1]},
    )
    assert resp.status_code == 201
    assert resp.json()["scores"]["extroversao"] == 7.0
    assert "Gosling" in resp.json()["instrumento"]


async def test_big_five_e_exclusivo_de_aluno(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    await criar_usuario(db_session, email="professor.bigfive@teste.com", papel=Papel.PROFESSOR)
    token = await _token(client, "professor.bigfive@teste.com")

    resp = await client.post(
        "/api/v1/me/big-five",
        headers=_auth(token),
        json={"respostas": [4] * 10},
    )
    assert resp.status_code == 400


async def test_big_five_resposta_fora_da_escala_e_rejeitada(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    await criar_usuario(db_session, email="aluno.escala@teste.com", papel=Papel.ALUNO)
    token = await _token(client, "aluno.escala@teste.com")

    resp = await client.post(
        "/api/v1/me/big-five",
        headers=_auth(token),
        json={"respostas": [8, 1, 7, 1, 7, 1, 7, 1, 7, 1]},
    )
    assert resp.status_code == 422


async def test_preferencias_acessibilidade_upsert(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    await criar_usuario(db_session, email="aluno.prefs@teste.com", papel=Papel.ALUNO)
    token = await _token(client, "aluno.prefs@teste.com")

    default = await client.get("/api/v1/me/preferencias-acessibilidade", headers=_auth(token))
    assert default.status_code == 200
    assert default.json()["tamanho_fonte"] == "medio"

    atualizado = await client.put(
        "/api/v1/me/preferencias-acessibilidade",
        headers=_auth(token),
        json={
            "fonte_legivel": True,
            "alto_contraste": True,
            "tempo_extra_percentual": 50,
            "leitura_voz_alta": False,
            "reducao_estimulos": True,
            "tamanho_fonte": "grande",
        },
    )
    assert atualizado.status_code == 200
    assert atualizado.json()["tamanho_fonte"] == "grande"

    confirmado = await client.get("/api/v1/me/preferencias-acessibilidade", headers=_auth(token))
    assert confirmado.json()["tempo_extra_percentual"] == 50
