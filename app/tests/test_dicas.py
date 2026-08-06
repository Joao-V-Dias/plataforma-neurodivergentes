"""Testes de aceite da Parte 6: motor de dicas progressivas.

O provedor de IA (Groq) e sempre mockado nestes testes - chamar a API real
custaria dinheiro e seria nao-deterministico, e o que precisamos validar e
a *orquestracao* (progressao de nivel, adaptacao de prompt por perfil,
registro de eficacia), nao a qualidade do texto gerado por um modelo de
terceiros. `app/tests/test_ai_prompts.py` cobre a engenharia de prompt
propriamente dita (que e pura e determinística) sem nenhum mock."""

from typing import Any

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.usuario import Papel
from app.repositories import perfil_big_five_repository
from app.tests.conftest import criar_instituicao, criar_turma, criar_usuario


async def _fake_gerar_texto(*, system_prompt: str, mensagem_usuario: str) -> str:
    """Substituto do motor de IA real: devolve o proprio system prompt, o
    que permite os testes verificarem, no conteudo persistido da dica, que
    a adaptacao de perfil realmente influenciou o texto que seria enviado
    ao modelo."""
    return system_prompt


@pytest.fixture(autouse=True)
def _mockar_groq(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("app.services.dica_service.gerar_texto", _fake_gerar_texto)


async def _token(client: AsyncClient, email: str, senha: str = "SenhaValida123") -> str:
    resp = await client.post("/api/v1/auth/login", json={"email": email, "senha": senha})
    assert resp.status_code == 200, resp.text
    return str(resp.json()["access_token"])


def _auth(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


async def _preparar_turma_com_problema(
    client: AsyncClient, db_session: AsyncSession, *, sufixo: str
) -> dict[str, Any]:
    instituicao = await criar_instituicao(db_session)
    professor = await criar_usuario(
        db_session, email=f"prof.dica.{sufixo}@teste.com", papel=Papel.PROFESSOR,
        instituicao_id=instituicao.id,
    )
    aluno = await criar_usuario(
        db_session, email=f"aluno.dica.{sufixo}@teste.com", papel=Papel.ALUNO,
        instituicao_id=instituicao.id,
    )
    turma = await criar_turma(
        db_session, instituicao_id=instituicao.id, professor_responsavel_id=professor.id
    )
    token_professor = await _token(client, f"prof.dica.{sufixo}@teste.com")

    problema_resp = await client.post(
        "/api/v1/problemas",
        headers=_auth(token_professor),
        json={
            "titulo": "Soma de dois numeros",
            "enunciado": "Leia dois inteiros e imprima a soma.",
            "linguagem": "python",
            "nivel_dificuldade": "facil",
            "tags_codigos": [],
            "casos": [{"entrada": "2 3", "saida_esperada": "5", "publico": True}],
        },
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
        "token_aluno": await _token(client, f"aluno.dica.{sufixo}@teste.com"),
    }


async def test_dica_progride_de_nivel_1_a_4_e_bloqueia_no_quinto_pedido(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    ctx = await _preparar_turma_com_problema(client, db_session, sufixo="progressao")

    for nivel_esperado in (1, 2, 3, 4):
        resp = await client.post(
            f"/api/v1/problemas/{ctx['problema_id']}/dicas", headers=_auth(ctx["token_aluno"])
        )
        assert resp.status_code == 201, resp.text
        assert resp.json()["nivel"] == nivel_esperado

    resp_extra = await client.post(
        f"/api/v1/problemas/{ctx['problema_id']}/dicas", headers=_auth(ctx["token_aluno"])
    )
    assert resp_extra.status_code == 409


async def test_aluno_nao_escolhe_o_nivel_endpoint_nao_aceita_esse_parametro(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    """O guardrail de "nunca pular etapa" e estrutural: o endpoint de
    solicitar dica nao tem corpo de requisicao, entao nao ha como o
    cliente pedir um nivel especifico - o servidor sempre calcula
    nivel_maximo_ja_dado + 1 (ver app/services/dica_service.py)."""
    ctx = await _preparar_turma_com_problema(client, db_session, sufixo="semescolha")

    resp = await client.post(
        f"/api/v1/problemas/{ctx['problema_id']}/dicas",
        headers=_auth(ctx["token_aluno"]),
        json={"nivel": 4},
    )
    assert resp.status_code == 201
    # corpo extra e simplesmente ignorado pelo FastAPI - a dica gerada e
    # sempre a de nivel 1, nunca a que o corpo "pediu".
    assert resp.json()["nivel"] == 1


async def test_minhas_dicas_lista_apenas_do_proprio_aluno_sem_dado_de_eficacia(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    ctx = await _preparar_turma_com_problema(client, db_session, sufixo="minhasdicas")

    await client.post(
        f"/api/v1/problemas/{ctx['problema_id']}/dicas", headers=_auth(ctx["token_aluno"])
    )

    resp = await client.get(
        f"/api/v1/problemas/{ctx['problema_id']}/minhas-dicas", headers=_auth(ctx["token_aluno"])
    )
    assert resp.status_code == 200
    dicas = resp.json()
    assert len(dicas) == 1
    assert "resolvida_apos" not in dicas[0]
    assert "adaptacoes_aplicadas" not in dicas[0]


async def test_professor_ve_eficacia_apos_submissao_aceita(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    ctx = await _preparar_turma_com_problema(client, db_session, sufixo="eficacia")

    dica_resp = await client.post(
        f"/api/v1/problemas/{ctx['problema_id']}/dicas", headers=_auth(ctx["token_aluno"])
    )
    assert dica_resp.status_code == 201

    submissao_resp = await client.post(
        f"/api/v1/problemas/{ctx['problema_id']}/submissoes",
        headers=_auth(ctx["token_aluno"]),
        json={"codigo_fonte": "a, b = map(int, input().split())\nprint(a + b)"},
    )
    assert submissao_resp.status_code == 201, submissao_resp.text
    assert submissao_resp.json()["status"] == "aceito"

    historico_resp = await client.get(
        f"/api/v1/problemas/{ctx['problema_id']}/dicas/{ctx['aluno'].id}",
        headers=_auth(ctx["token_professor"]),
    )
    assert historico_resp.status_code == 200
    historico = historico_resp.json()
    assert len(historico) == 1
    assert historico[0]["resolvida_apos"] is True
    assert historico[0]["tempo_ate_resolver_ms"] is not None
    assert historico[0]["tempo_ate_resolver_ms"] >= 0


async def test_aluno_nao_acessa_historico_de_dicas_de_outro_aluno(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    ctx = await _preparar_turma_com_problema(client, db_session, sufixo="isolamento")

    resp = await client.get(
        f"/api/v1/problemas/{ctx['problema_id']}/dicas/{ctx['aluno'].id}",
        headers=_auth(ctx["token_aluno"]),
    )
    assert resp.status_code == 403


async def test_sem_groq_api_key_endpoint_devolve_503(
    client: AsyncClient, db_session: AsyncSession, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Sem chave configurada (GROQ_API_KEY vazia no .env de teste), o
    motor real (app/ai/groq_client.py) deve recusar de forma controlada -
    nunca deixar a excecao do SDK vazar como 500 generico. Restauramos a
    funcao real por cima do mock global desta suite (fixture
    `_mockar_groq`) so para este teste."""
    import app.services.dica_service as dica_service_module
    from app.ai.groq_client import gerar_texto as gerar_texto_real
    from app.core.config import get_settings

    assert not get_settings().groq_api_key, (
        "este teste assume GROQ_API_KEY vazia no ambiente de teste"
    )
    monkeypatch.setattr(dica_service_module, "gerar_texto", gerar_texto_real)

    ctx = await _preparar_turma_com_problema(client, db_session, sufixo="semchave")
    resp = await client.post(
        f"/api/v1/problemas/{ctx['problema_id']}/dicas", headers=_auth(ctx["token_aluno"])
    )
    assert resp.status_code == 503


async def test_dois_alunos_perfis_diferentes_recebem_dicas_com_tom_distinto(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    """Criterio de aceite da Parte 6: dois alunos com perfis diferentes
    recebendo o mesmo problema devem receber dicas com tom/estrutura
    visivelmente distintos."""
    ctx = await _preparar_turma_com_problema(client, db_session, sufixo="tomdistinto")

    instituicao_id = ctx["aluno"].instituicao_id
    aluno_tea = await criar_usuario(
        db_session, email="aluno.dica.tomdistinto.tea@teste.com", papel=Papel.ALUNO,
        instituicao_id=instituicao_id,
    )
    await client.post(
        f"/api/v1/turmas/{ctx['turma'].id}/matriculas",
        headers=_auth(ctx["token_professor"]),
        json={"aluno_id": str(aluno_tea.id)},
    )
    token_tea = await _token(client, "aluno.dica.tomdistinto.tea@teste.com")

    # Aluno 1: TDAH.
    resp_perfil_tdah = await client.post(
        f"/api/v1/alunos/{ctx['aluno'].id}/perfil",
        headers=_auth(ctx["token_aluno"]),
        json={"condicoes_codigos": ["tdah"], "aceite_consentimento": True},
    )
    assert resp_perfil_tdah.status_code == 201, resp_perfil_tdah.text

    # Aluno 2: TEA.
    resp_perfil_tea = await client.post(
        f"/api/v1/alunos/{aluno_tea.id}/perfil",
        headers=_auth(token_tea),
        json={"condicoes_codigos": ["tea"], "aceite_consentimento": True},
    )
    assert resp_perfil_tea.status_code == 201, resp_perfil_tea.text

    dica_tdah = await client.post(
        f"/api/v1/problemas/{ctx['problema_id']}/dicas", headers=_auth(ctx["token_aluno"])
    )
    dica_tea = await client.post(
        f"/api/v1/problemas/{ctx['problema_id']}/dicas", headers=_auth(token_tea)
    )
    assert dica_tdah.status_code == 201
    assert dica_tea.status_code == 201

    conteudo_tdah = dica_tdah.json()["conteudo"]
    conteudo_tea = dica_tea.json()["conteudo"]

    assert conteudo_tdah != conteudo_tea
    assert "frases curtas, quebradas em passos" in conteudo_tdah
    assert "linguagem literal e direta" in conteudo_tea
    assert "linguagem literal e direta" not in conteudo_tdah
    assert "frases curtas, quebradas em passos" not in conteudo_tea

    # Log de auditoria (Professor+) mostra as adaptacoes realmente
    # aplicadas por aluno - a prova de que a diferenca de tom nao e
    # acidental, e sim rastreavel.
    hist_tdah = await client.get(
        f"/api/v1/problemas/{ctx['problema_id']}/dicas/{ctx['aluno'].id}",
        headers=_auth(ctx["token_professor"]),
    )
    hist_tea = await client.get(
        f"/api/v1/problemas/{ctx['problema_id']}/dicas/{aluno_tea.id}",
        headers=_auth(ctx["token_professor"]),
    )
    assert hist_tdah.json()[0]["adaptacoes_aplicadas"] == ["tdah_passos_curtos"]
    assert hist_tea.json()[0]["adaptacoes_aplicadas"] == ["tea_linguagem_literal"]


async def test_big_five_neuroticismo_alto_adapta_tom_para_tranquilizador(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    ctx = await _preparar_turma_com_problema(client, db_session, sufixo="neuroticismo")

    await perfil_big_five_repository.create_versao(
        db_session,
        aluno_id=ctx["aluno"].id,
        versao=1,
        scores={
            "abertura": 4.0,
            "conscienciosidade": 4.0,
            "extroversao": 4.0,
            "amabilidade": 4.0,
            "neuroticismo": 6.5,
        },
        respostas_brutas=[4, 4, 4, 4, 4, 4, 4, 4, 6, 7],
    )

    resp = await client.post(
        f"/api/v1/problemas/{ctx['problema_id']}/dicas", headers=_auth(ctx["token_aluno"])
    )
    assert resp.status_code == 201
    assert "tom tranquilizador" in resp.json()["conteudo"]

    hist = await client.get(
        f"/api/v1/problemas/{ctx['problema_id']}/dicas/{ctx['aluno'].id}",
        headers=_auth(ctx["token_professor"]),
    )
    assert hist.json()[0]["adaptacoes_aplicadas"] == ["neuroticismo_alto_tom_tranquilizador"]
