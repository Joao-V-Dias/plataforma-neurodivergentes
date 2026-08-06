"""Testes de aceite da Parte 4: professor cria turma, matricula alunos e
lista progresso agregado; aluno nao enxerga dados de outras turmas;
visibilidade por papel (professor so suas turmas, coordenador/diretor
toda a instituicao)."""

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


async def test_professor_cria_turma_matricula_e_ve_progresso(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    instituicao = await criar_instituicao(db_session)
    professor = await criar_usuario(
        db_session, email="professor.fluxo@teste.com", papel=Papel.PROFESSOR,
        instituicao_id=instituicao.id,
    )
    aluno = await criar_usuario(
        db_session, email="aluno.fluxo@teste.com", papel=Papel.ALUNO,
        instituicao_id=instituicao.id,
    )
    token = await _token(client, "professor.fluxo@teste.com")

    turma_resp = await client.post(
        "/api/v1/turmas",
        headers=_auth(token),
        json={
            "nome": "Introducao a Programacao",
            "periodo": "2026.1",
            "professor_responsavel_id": str(professor.id),
        },
    )
    assert turma_resp.status_code == 201, turma_resp.text
    turma_id = turma_resp.json()["id"]

    matricula_resp = await client.post(
        f"/api/v1/turmas/{turma_id}/matriculas",
        headers=_auth(token),
        json={"aluno_id": str(aluno.id)},
    )
    assert matricula_resp.status_code == 201, matricula_resp.text
    assert matricula_resp.json()["aluno_nome"] == aluno.nome

    progresso_resp = await client.get(
        f"/api/v1/turmas/{turma_id}/progresso", headers=_auth(token)
    )
    assert progresso_resp.status_code == 200
    progresso = progresso_resp.json()
    assert len(progresso) == 1
    assert progresso[0]["aluno_id"] == str(aluno.id)


async def test_criar_turma_professor_responsavel_deve_ser_professor(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    instituicao = await criar_instituicao(db_session)
    coordenador = await criar_usuario(
        db_session, email="coord.turma@teste.com", papel=Papel.COORDENADOR,
        instituicao_id=instituicao.id,
    )
    token = await _token(client, "coord.turma@teste.com")

    resp = await client.post(
        "/api/v1/turmas",
        headers=_auth(token),
        json={
            "nome": "Turma Invalida",
            "periodo": "2026.1",
            "professor_responsavel_id": str(coordenador.id),
        },
    )
    assert resp.status_code == 400


async def test_criar_turma_professor_de_outra_instituicao(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    inst_a = await criar_instituicao(db_session)
    inst_b = await criar_instituicao(db_session)
    await criar_usuario(
        db_session, email="diretor.turma@teste.com", papel=Papel.DIRETOR, instituicao_id=inst_a.id
    )
    professor_outra = await criar_usuario(
        db_session, email="professor.outra@teste.com", papel=Papel.PROFESSOR,
        instituicao_id=inst_b.id,
    )
    token = await _token(client, "diretor.turma@teste.com")

    resp = await client.post(
        "/api/v1/turmas",
        headers=_auth(token),
        json={
            "nome": "Turma Cross-Tenant",
            "periodo": "2026.1",
            "professor_responsavel_id": str(professor_outra.id),
        },
    )
    assert resp.status_code == 403


async def test_professor_sem_vinculo_nao_acessa_turma(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    instituicao = await criar_instituicao(db_session)
    titular = await criar_usuario(
        db_session, email="titular@teste.com", papel=Papel.PROFESSOR, instituicao_id=instituicao.id
    )
    await criar_usuario(
        db_session, email="outro.prof@teste.com", papel=Papel.PROFESSOR,
        instituicao_id=instituicao.id,
    )
    turma = await criar_turma(
        db_session, instituicao_id=instituicao.id, professor_responsavel_id=titular.id
    )
    token_outro = await _token(client, "outro.prof@teste.com")

    resp = await client.get(f"/api/v1/turmas/{turma.id}", headers=_auth(token_outro))
    assert resp.status_code == 403

    lista = await client.get("/api/v1/turmas", headers=_auth(token_outro))
    assert lista.json() == []


async def test_coordenador_ve_todas_turmas_da_instituicao(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    instituicao = await criar_instituicao(db_session)
    professor = await criar_usuario(
        db_session, email="prof.coord.ve@teste.com", papel=Papel.PROFESSOR,
        instituicao_id=instituicao.id,
    )
    await criar_usuario(
        db_session, email="coordenador.ve@teste.com", papel=Papel.COORDENADOR,
        instituicao_id=instituicao.id,
    )
    turma = await criar_turma(
        db_session, instituicao_id=instituicao.id, professor_responsavel_id=professor.id
    )
    token = await _token(client, "coordenador.ve@teste.com")

    resp = await client.get(f"/api/v1/turmas/{turma.id}", headers=_auth(token))
    assert resp.status_code == 200

    lista = await client.get("/api/v1/turmas", headers=_auth(token))
    assert len(lista.json()) == 1


async def test_turma_de_outra_instituicao_e_404(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    inst_a = await criar_instituicao(db_session)
    inst_b = await criar_instituicao(db_session)
    professor_b = await criar_usuario(
        db_session, email="prof.instB@teste.com", papel=Papel.PROFESSOR, instituicao_id=inst_b.id
    )
    turma_b = await criar_turma(
        db_session, instituicao_id=inst_b.id, professor_responsavel_id=professor_b.id
    )
    await criar_usuario(
        db_session, email="diretor.instA@teste.com", papel=Papel.DIRETOR, instituicao_id=inst_a.id
    )
    token = await _token(client, "diretor.instA@teste.com")

    resp = await client.get(f"/api/v1/turmas/{turma_b.id}", headers=_auth(token))
    assert resp.status_code == 404


async def test_matricula_duplicada_e_rejeitada(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    instituicao = await criar_instituicao(db_session)
    professor = await criar_usuario(
        db_session, email="prof.dup@teste.com", papel=Papel.PROFESSOR, instituicao_id=instituicao.id
    )
    aluno = await criar_usuario(
        db_session, email="aluno.dup@teste.com", papel=Papel.ALUNO, instituicao_id=instituicao.id
    )
    turma = await criar_turma(
        db_session, instituicao_id=instituicao.id, professor_responsavel_id=professor.id
    )
    token = await _token(client, "prof.dup@teste.com")

    await client.post(
        f"/api/v1/turmas/{turma.id}/matriculas", headers=_auth(token),
        json={"aluno_id": str(aluno.id)},
    )
    resp = await client.post(
        f"/api/v1/turmas/{turma.id}/matriculas", headers=_auth(token),
        json={"aluno_id": str(aluno.id)},
    )
    assert resp.status_code == 409


async def test_matricular_usuario_que_nao_e_aluno_falha(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    instituicao = await criar_instituicao(db_session)
    professor = await criar_usuario(
        db_session, email="prof.naoaluno@teste.com", papel=Papel.PROFESSOR,
        instituicao_id=instituicao.id,
    )
    outro_professor = await criar_usuario(
        db_session, email="outro.naoaluno@teste.com", papel=Papel.PROFESSOR,
        instituicao_id=instituicao.id,
    )
    turma = await criar_turma(
        db_session, instituicao_id=instituicao.id, professor_responsavel_id=professor.id
    )
    token = await _token(client, "prof.naoaluno@teste.com")

    resp = await client.post(
        f"/api/v1/turmas/{turma.id}/matriculas", headers=_auth(token),
        json={"aluno_id": str(outro_professor.id)},
    )
    assert resp.status_code == 400


async def test_desmatricula_e_permite_rematricula(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    instituicao = await criar_instituicao(db_session)
    professor = await criar_usuario(
        db_session, email="prof.desmat@teste.com", papel=Papel.PROFESSOR,
        instituicao_id=instituicao.id,
    )
    aluno = await criar_usuario(
        db_session, email="aluno.desmat@teste.com", papel=Papel.ALUNO,
        instituicao_id=instituicao.id,
    )
    turma = await criar_turma(
        db_session, instituicao_id=instituicao.id, professor_responsavel_id=professor.id
    )
    token = await _token(client, "prof.desmat@teste.com")

    await client.post(
        f"/api/v1/turmas/{turma.id}/matriculas", headers=_auth(token),
        json={"aluno_id": str(aluno.id)},
    )
    desmat = await client.delete(
        f"/api/v1/turmas/{turma.id}/matriculas/{aluno.id}", headers=_auth(token)
    )
    assert desmat.status_code == 204

    lista = await client.get(f"/api/v1/turmas/{turma.id}/matriculas", headers=_auth(token))
    assert lista.json() == []

    rematricula = await client.post(
        f"/api/v1/turmas/{turma.id}/matriculas", headers=_auth(token),
        json={"aluno_id": str(aluno.id)},
    )
    assert rematricula.status_code == 201


async def test_adicionar_professor_co_docencia(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    instituicao = await criar_instituicao(db_session)
    titular = await criar_usuario(
        db_session, email="titular.codoc@teste.com", papel=Papel.PROFESSOR,
        instituicao_id=instituicao.id,
    )
    co_professor = await criar_usuario(
        db_session, email="co.docente@teste.com", papel=Papel.PROFESSOR,
        instituicao_id=instituicao.id,
    )
    turma = await criar_turma(
        db_session, instituicao_id=instituicao.id, professor_responsavel_id=titular.id
    )
    token_titular = await _token(client, "titular.codoc@teste.com")

    resp = await client.post(
        f"/api/v1/turmas/{turma.id}/professores", headers=_auth(token_titular),
        json={"professor_id": str(co_professor.id)},
    )
    assert resp.status_code == 204

    token_co = await _token(client, "co.docente@teste.com")
    detalhe = await client.get(f"/api/v1/turmas/{turma.id}", headers=_auth(token_co))
    assert detalhe.status_code == 200
    assert detalhe.json()["total_professores"] == 2


async def test_aluno_nao_acessa_endpoint_de_gestao_da_turma(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    instituicao = await criar_instituicao(db_session)
    professor = await criar_usuario(
        db_session, email="prof.alunobloq@teste.com", papel=Papel.PROFESSOR,
        instituicao_id=instituicao.id,
    )
    await criar_usuario(
        db_session, email="aluno.bloq@teste.com", papel=Papel.ALUNO, instituicao_id=instituicao.id
    )
    turma = await criar_turma(
        db_session, instituicao_id=instituicao.id, professor_responsavel_id=professor.id
    )
    token = await _token(client, "aluno.bloq@teste.com")

    resp = await client.get(f"/api/v1/turmas/{turma.id}", headers=_auth(token))
    assert resp.status_code == 403

    resp_lista = await client.get("/api/v1/turmas", headers=_auth(token))
    assert resp_lista.status_code == 403


async def test_aluno_ve_apenas_suas_proprias_turmas(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    instituicao = await criar_instituicao(db_session)
    professor = await criar_usuario(
        db_session, email="prof.isolamento@teste.com", papel=Papel.PROFESSOR,
        instituicao_id=instituicao.id,
    )
    aluno = await criar_usuario(
        db_session, email="aluno.isolamento@teste.com", papel=Papel.ALUNO,
        instituicao_id=instituicao.id,
    )
    turma_matriculada = await criar_turma(
        db_session, instituicao_id=instituicao.id, professor_responsavel_id=professor.id,
        nome="Turma A",
    )
    turma_nao_matriculada = await criar_turma(
        db_session, instituicao_id=instituicao.id, professor_responsavel_id=professor.id,
        nome="Turma B",
    )
    token_professor = await _token(client, "prof.isolamento@teste.com")
    await client.post(
        f"/api/v1/turmas/{turma_matriculada.id}/matriculas",
        headers=_auth(token_professor),
        json={"aluno_id": str(aluno.id)},
    )

    token_aluno = await _token(client, "aluno.isolamento@teste.com")
    minhas_turmas = await client.get("/api/v1/me/turmas", headers=_auth(token_aluno))
    ids = {t["id"] for t in minhas_turmas.json()}
    assert ids == {str(turma_matriculada.id)}
    assert str(turma_nao_matriculada.id) not in ids

    progresso_nao_matriculada = await client.get(
        f"/api/v1/me/turmas/{turma_nao_matriculada.id}/progresso", headers=_auth(token_aluno)
    )
    assert progresso_nao_matriculada.status_code == 404
