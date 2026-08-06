"""Testes de aceite da Parte 5: professor cadastra problema com casos
publicos/ocultos; aluno submete codigo, execucao isolada com timeout;
resposta nunca expoe detalhes internos do sandbox nem de caso oculto;
acesso controlado por matricula em turma vinculada ao problema.

Estes testes executam codigo de verdade dentro de containers Docker
efemeros (app/sandbox/executor.py) - mais lentos que testes normais, mas
sao o unico jeito honesto de validar o criterio de aceite "execucao
ocorre isolada com timeout"."""

from typing import Any

from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.usuario import Papel
from app.tests.conftest import criar_instituicao, criar_turma, criar_usuario


async def _token(client: AsyncClient, email: str, senha: str = "SenhaValida123") -> str:
    resp = await client.post("/api/v1/auth/login", json={"email": email, "senha": senha})
    assert resp.status_code == 200, resp.text
    return str(resp.json()["access_token"])


def _auth(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def _payload_problema(**overrides: Any) -> dict[str, Any]:
    base: dict[str, Any] = {
        "titulo": "Dobro de um numero",
        "enunciado": "Leia um inteiro e imprima o dobro.",
        "linguagem": "python",
        "nivel_dificuldade": "facil",
        "tags_codigos": ["loops"],
        "casos": [
            {"entrada": "5", "saida_esperada": "10", "publico": True},
            {"entrada": "100", "saida_esperada": "200", "publico": False},
        ],
    }
    base.update(overrides)
    return base


async def _preparar_turma_com_problema(
    client: AsyncClient, db_session: AsyncSession, *, sufixo: str
) -> dict[str, Any]:
    instituicao = await criar_instituicao(db_session)
    professor = await criar_usuario(
        db_session, email=f"prof.{sufixo}@teste.com", papel=Papel.PROFESSOR,
        instituicao_id=instituicao.id,
    )
    aluno = await criar_usuario(
        db_session, email=f"aluno.{sufixo}@teste.com", papel=Papel.ALUNO,
        instituicao_id=instituicao.id,
    )
    turma = await criar_turma(
        db_session, instituicao_id=instituicao.id, professor_responsavel_id=professor.id
    )
    token_professor = await _token(client, f"prof.{sufixo}@teste.com")

    problema_resp = await client.post(
        "/api/v1/problemas", headers=_auth(token_professor), json=_payload_problema()
    )
    assert problema_resp.status_code == 201, problema_resp.text
    problema_id = problema_resp.json()["id"]

    await client.post(
        f"/api/v1/problemas/{problema_id}/turmas",
        headers=_auth(token_professor),
        json={"turma_id": str(turma.id)},
    )
    await client.post(
        f"/api/v1/turmas/{turma.id}/matriculas",
        headers=_auth(token_professor),
        json={"aluno_id": str(aluno.id)},
    )

    return {
        "professor": professor,
        "aluno": aluno,
        "turma": turma,
        "problema_id": problema_id,
        "token_professor": token_professor,
        "token_aluno": await _token(client, f"aluno.{sufixo}@teste.com"),
    }


async def test_professor_cria_problema_com_casos_publicos_e_ocultos(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    instituicao = await criar_instituicao(db_session)
    await criar_usuario(
        db_session, email="prof.criacao@teste.com", papel=Papel.PROFESSOR,
        instituicao_id=instituicao.id,
    )
    token = await _token(client, "prof.criacao@teste.com")

    resp = await client.post("/api/v1/problemas", headers=_auth(token), json=_payload_problema())
    assert resp.status_code == 201, resp.text
    body = resp.json()
    assert body["titulo"] == "Dobro de um numero"
    assert len(body["tags"]) == 1


async def test_criar_problema_linguagem_nao_suportada(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    instituicao = await criar_instituicao(db_session)
    await criar_usuario(
        db_session, email="prof.linguagem@teste.com", papel=Papel.PROFESSOR,
        instituicao_id=instituicao.id,
    )
    token = await _token(client, "prof.linguagem@teste.com")

    resp = await client.post(
        "/api/v1/problemas", headers=_auth(token), json=_payload_problema(linguagem="cobol")
    )
    assert resp.status_code == 400


async def test_criar_problema_tag_invalida(client: AsyncClient, db_session: AsyncSession) -> None:
    instituicao = await criar_instituicao(db_session)
    await criar_usuario(
        db_session, email="prof.tag@teste.com", papel=Papel.PROFESSOR,
        instituicao_id=instituicao.id,
    )
    token = await _token(client, "prof.tag@teste.com")

    resp = await client.post(
        "/api/v1/problemas",
        headers=_auth(token),
        json=_payload_problema(tags_codigos=["nao-existe"]),
    )
    assert resp.status_code == 422


async def test_aluno_sem_turma_vinculada_nao_acessa_problema(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    instituicao = await criar_instituicao(db_session)
    await criar_usuario(
        db_session, email="prof.semturma@teste.com", papel=Papel.PROFESSOR,
        instituicao_id=instituicao.id,
    )
    await criar_usuario(
        db_session, email="aluno.semturma@teste.com", papel=Papel.ALUNO,
        instituicao_id=instituicao.id,
    )
    token_professor = await _token(client, "prof.semturma@teste.com")
    problema_resp = await client.post(
        "/api/v1/problemas", headers=_auth(token_professor), json=_payload_problema()
    )
    problema_id = problema_resp.json()["id"]

    token_aluno = await _token(client, "aluno.semturma@teste.com")
    resp = await client.get(f"/api/v1/problemas/{problema_id}", headers=_auth(token_aluno))
    assert resp.status_code == 403


async def test_aluno_submete_codigo_correto_recebe_aceito(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    ctx = await _preparar_turma_com_problema(client, db_session, sufixo="aceito")

    resp = await client.post(
        f"/api/v1/problemas/{ctx['problema_id']}/submissoes",
        headers=_auth(ctx["token_aluno"]),
        json={"codigo_fonte": "print(int(input()) * 2)"},
    )
    assert resp.status_code == 201, resp.text
    body = resp.json()
    assert body["status"] == "aceito"
    assert len(body["resultados"]) == 2
    assert all(r["passou"] for r in body["resultados"])


async def test_aluno_submete_codigo_errado_recebe_reprovado(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    ctx = await _preparar_turma_com_problema(client, db_session, sufixo="reprovado")

    resp = await client.post(
        f"/api/v1/problemas/{ctx['problema_id']}/submissoes",
        headers=_auth(ctx["token_aluno"]),
        json={"codigo_fonte": "print(int(input()) * 3)"},
    )
    assert resp.status_code == 201
    assert resp.json()["status"] == "reprovado"


async def test_resposta_nao_expoe_detalhes_de_caso_oculto(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    ctx = await _preparar_turma_com_problema(client, db_session, sufixo="oculto")

    resp = await client.post(
        f"/api/v1/problemas/{ctx['problema_id']}/submissoes",
        headers=_auth(ctx["token_aluno"]),
        json={"codigo_fonte": "print(int(input()) * 2)"},
    )
    resultados = resp.json()["resultados"]
    publico = next(r for r in resultados if r["publico"])
    oculto = next(r for r in resultados if not r["publico"])

    assert publico["entrada"] == "5"
    assert publico["saida_esperada"] == "10"
    assert publico["saida_obtida"] is not None

    assert oculto["entrada"] is None
    assert oculto["saida_esperada"] is None
    assert oculto["saida_obtida"] is None
    assert oculto["erro"] is None
    # mas o professor ainda sabe se passou ou nao, para poder corrigir
    assert oculto["passou"] is True


async def test_resposta_de_erro_nunca_expoe_caminho_do_sandbox(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    ctx = await _preparar_turma_com_problema(client, db_session, sufixo="erro")

    resp = await client.post(
        f"/api/v1/problemas/{ctx['problema_id']}/submissoes",
        headers=_auth(ctx["token_aluno"]),
        json={"codigo_fonte": "raise ValueError('boom')"},
    )
    assert resp.status_code == 201
    body = resp.json()
    assert body["status"] == "erro_execucao"
    publico = next(r for r in body["resultados"] if r["publico"])
    assert publico["erro"] is not None
    assert "/sandbox" not in publico["erro"]
    assert "solucao.py" not in publico["erro"]
    assert "Traceback" not in publico["erro"]


async def test_execucao_com_loop_infinito_e_interrompida_por_timeout(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    ctx = await _preparar_turma_com_problema(client, db_session, sufixo="timeout")

    resp = await client.post(
        f"/api/v1/problemas/{ctx['problema_id']}/submissoes",
        headers=_auth(ctx["token_aluno"]),
        json={"codigo_fonte": "while True:\n    pass"},
    )
    assert resp.status_code == 201
    assert resp.json()["status"] == "tempo_excedido"


async def test_professor_ve_casos_ocultos_aluno_nao_ve(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    ctx = await _preparar_turma_com_problema(client, db_session, sufixo="visibilidade")

    resp_prof = await client.get(
        f"/api/v1/problemas/{ctx['problema_id']}", headers=_auth(ctx["token_professor"])
    )
    resp_aluno = await client.get(
        f"/api/v1/problemas/{ctx['problema_id']}", headers=_auth(ctx["token_aluno"])
    )

    assert len(resp_prof.json()["casos"]) == 2
    assert len(resp_aluno.json()["casos"]) == 1
    assert resp_aluno.json()["casos"][0]["publico"] is True


async def test_historico_submissoes_aluno_ve_apenas_proprias(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    ctx = await _preparar_turma_com_problema(client, db_session, sufixo="historico")

    await client.post(
        f"/api/v1/problemas/{ctx['problema_id']}/submissoes",
        headers=_auth(ctx["token_aluno"]),
        json={"codigo_fonte": "print(int(input()) * 2)"},
    )

    minhas = await client.get(
        f"/api/v1/problemas/{ctx['problema_id']}/minhas-submissoes",
        headers=_auth(ctx["token_aluno"]),
    )
    assert len(minhas.json()) == 1

    todas = await client.get(
        f"/api/v1/problemas/{ctx['problema_id']}/submissoes",
        headers=_auth(ctx["token_professor"]),
    )
    assert len(todas.json()) == 1

    aluno_nao_pode_ver_todas = await client.get(
        f"/api/v1/problemas/{ctx['problema_id']}/submissoes", headers=_auth(ctx["token_aluno"])
    )
    assert aluno_nao_pode_ver_todas.status_code == 403


async def test_progresso_turma_reflete_submissoes_reais(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    ctx = await _preparar_turma_com_problema(client, db_session, sufixo="progresso")

    await client.post(
        f"/api/v1/problemas/{ctx['problema_id']}/submissoes",
        headers=_auth(ctx["token_aluno"]),
        json={"codigo_fonte": "print(int(input()) * 3)"},
    )
    await client.post(
        f"/api/v1/problemas/{ctx['problema_id']}/submissoes",
        headers=_auth(ctx["token_aluno"]),
        json={"codigo_fonte": "print(int(input()) * 2)"},
    )

    progresso = await client.get(
        f"/api/v1/turmas/{ctx['turma'].id}/progresso", headers=_auth(ctx["token_professor"])
    )
    assert progresso.status_code == 200
    dados = progresso.json()[0]
    assert dados["tentativas"] == 2
    assert dados["problemas_resolvidos"] == 1


async def test_aluno_matriculado_lista_problemas_da_propria_turma(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    ctx = await _preparar_turma_com_problema(client, db_session, sufixo="turmaproblemas")

    resp_aluno = await client.get(
        f"/api/v1/turmas/{ctx['turma'].id}/problemas", headers=_auth(ctx["token_aluno"])
    )
    assert resp_aluno.status_code == 200
    ids = [p["id"] for p in resp_aluno.json()]
    assert ctx["problema_id"] in ids

    resp_professor = await client.get(
        f"/api/v1/turmas/{ctx['turma'].id}/problemas", headers=_auth(ctx["token_professor"])
    )
    assert resp_professor.status_code == 200
    assert ctx["problema_id"] in [p["id"] for p in resp_professor.json()]


async def test_aluno_nao_matriculado_nao_lista_problemas_da_turma(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    ctx = await _preparar_turma_com_problema(client, db_session, sufixo="turmasemacesso")
    instituicao_id = ctx["professor"].instituicao_id
    await criar_usuario(
        db_session, email="aluno.foraturma@teste.com", papel=Papel.ALUNO,
        instituicao_id=instituicao_id,
    )
    token_outro = await _token(client, "aluno.foraturma@teste.com")

    resp = await client.get(
        f"/api/v1/turmas/{ctx['turma'].id}/problemas", headers=_auth(token_outro)
    )
    assert resp.status_code == 403
