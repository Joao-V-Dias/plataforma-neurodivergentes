"""Gestao academica: CRUD de turma, co-docencia, matricula/desmatricula de
aluno e progresso agregado (placeholder ate a Parte 5)."""

import uuid

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_client_ip, get_current_user, get_turma_acessivel, require_min_role
from app.core.database import get_db
from app.models.turma import Turma
from app.models.usuario import Papel, Usuario
from app.repositories import matricula_repository, turma_repository
from app.schemas.turmas import (
    AdicionarProfessorRequest,
    CriarTurmaRequest,
    MatriculaResponse,
    MatricularRequest,
    ProgressoAlunoResponse,
    TurmaDetalheResponse,
    TurmaResponse,
)
from app.services import matricula_service, progresso_service, turma_service
from app.services.exceptions import (
    AlvoInvalidoError,
    InstituicaoDiferenteError,
    MatriculaDuplicadaError,
    RecursoNaoEncontradoError,
)

router = APIRouter(tags=["turmas"])


def _turma_detalhe_response(detalhe: turma_service.TurmaDetalhada) -> TurmaDetalheResponse:
    return TurmaDetalheResponse(
        **TurmaResponse.model_validate(detalhe.turma).model_dump(),
        total_professores=detalhe.total_professores,
        total_alunos_ativos=detalhe.total_alunos_ativos,
    )


def _matricula_response(item: matricula_service.MatriculaComAluno) -> MatriculaResponse:
    return MatriculaResponse(
        id=item.matricula.id,
        turma_id=item.matricula.turma_id,
        aluno_id=item.matricula.aluno_id,
        aluno_nome=item.aluno.nome,
        aluno_email=item.aluno.email,
        ativo=item.matricula.ativo,
        matriculado_em=item.matricula.matriculado_em,
        desmatriculado_em=item.matricula.desmatriculado_em,
    )


@router.post("/turmas", response_model=TurmaResponse, status_code=status.HTTP_201_CREATED)
async def criar_turma(
    payload: CriarTurmaRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
    criador: Usuario = Depends(require_min_role(Papel.PROFESSOR)),
) -> Turma:
    try:
        return await turma_service.criar_turma(
            db,
            criador=criador,
            nome=payload.nome,
            periodo=payload.periodo,
            professor_responsavel_id=payload.professor_responsavel_id,
            ip_address=get_client_ip(request),
        )
    except RecursoNaoEncontradoError as exc:
        raise HTTPException(status.HTTP_404_NOT_FOUND, str(exc)) from exc
    except AlvoInvalidoError as exc:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, str(exc)) from exc
    except InstituicaoDiferenteError as exc:
        raise HTTPException(status.HTTP_403_FORBIDDEN, str(exc)) from exc


@router.get("/turmas", response_model=list[TurmaResponse])
async def listar_turmas(
    db: AsyncSession = Depends(get_db),
    usuario: Usuario = Depends(require_min_role(Papel.PROFESSOR)),
) -> list[Turma]:
    """Professor ve so suas turmas vinculadas; Coordenador/Diretor veem
    todas as turmas da instituicao."""
    return list(await turma_service.listar_turmas_visiveis(db, usuario))


@router.get("/turmas/{turma_id}", response_model=TurmaDetalheResponse)
async def obter_turma(
    db: AsyncSession = Depends(get_db),
    turma: Turma = Depends(get_turma_acessivel),
) -> TurmaDetalheResponse:
    detalhe = await turma_service.obter_detalhe(db, turma)
    return _turma_detalhe_response(detalhe)


@router.post("/turmas/{turma_id}/professores", status_code=status.HTTP_204_NO_CONTENT)
async def adicionar_professor(
    payload: AdicionarProfessorRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
    turma: Turma = Depends(get_turma_acessivel),
    ator: Usuario = Depends(get_current_user),
) -> None:
    try:
        await turma_service.adicionar_professor(
            db,
            ator=ator,
            turma=turma,
            professor_id=payload.professor_id,
            ip_address=get_client_ip(request),
        )
    except RecursoNaoEncontradoError as exc:
        raise HTTPException(status.HTTP_404_NOT_FOUND, str(exc)) from exc
    except AlvoInvalidoError as exc:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, str(exc)) from exc
    except InstituicaoDiferenteError as exc:
        raise HTTPException(status.HTTP_403_FORBIDDEN, str(exc)) from exc


@router.post(
    "/turmas/{turma_id}/matriculas",
    response_model=MatriculaResponse,
    status_code=status.HTTP_201_CREATED,
)
async def matricular_aluno(
    payload: MatricularRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
    turma: Turma = Depends(get_turma_acessivel),
    ator: Usuario = Depends(get_current_user),
) -> MatriculaResponse:
    try:
        item = await matricula_service.matricular(
            db,
            ator=ator,
            turma=turma,
            aluno_id=payload.aluno_id,
            ip_address=get_client_ip(request),
        )
    except RecursoNaoEncontradoError as exc:
        raise HTTPException(status.HTTP_404_NOT_FOUND, str(exc)) from exc
    except AlvoInvalidoError as exc:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, str(exc)) from exc
    except InstituicaoDiferenteError as exc:
        raise HTTPException(status.HTTP_403_FORBIDDEN, str(exc)) from exc
    except MatriculaDuplicadaError as exc:
        raise HTTPException(status.HTTP_409_CONFLICT, str(exc)) from exc

    return _matricula_response(item)


@router.delete("/turmas/{turma_id}/matriculas/{aluno_id}", status_code=status.HTTP_204_NO_CONTENT)
async def desmatricular_aluno(
    aluno_id: uuid.UUID,
    request: Request,
    db: AsyncSession = Depends(get_db),
    turma: Turma = Depends(get_turma_acessivel),
    ator: Usuario = Depends(get_current_user),
) -> None:
    try:
        await matricula_service.desmatricular(
            db, ator=ator, turma=turma, aluno_id=aluno_id, ip_address=get_client_ip(request)
        )
    except RecursoNaoEncontradoError as exc:
        raise HTTPException(status.HTTP_404_NOT_FOUND, str(exc)) from exc


@router.get("/turmas/{turma_id}/matriculas", response_model=list[MatriculaResponse])
async def listar_matriculas(
    db: AsyncSession = Depends(get_db),
    turma: Turma = Depends(get_turma_acessivel),
) -> list[MatriculaResponse]:
    itens = await matricula_service.listar_matriculados(db, turma.id)
    return [_matricula_response(item) for item in itens]


@router.get("/turmas/{turma_id}/progresso", response_model=list[ProgressoAlunoResponse])
async def obter_progresso_turma(
    db: AsyncSession = Depends(get_db),
    turma: Turma = Depends(get_turma_acessivel),
) -> list[ProgressoAlunoResponse]:
    progresso = await progresso_service.obter_progresso_turma(db, turma.id)
    return [
        ProgressoAlunoResponse(
            aluno_id=p.aluno.id,
            aluno_nome=p.aluno.nome,
            problemas_resolvidos=p.problemas_resolvidos,
            tentativas=p.tentativas,
            tempo_gasto_minutos=p.tempo_gasto_minutos,
        )
        for p in progresso
    ]


@router.get("/me/turmas", response_model=list[TurmaResponse])
async def listar_minhas_turmas(
    db: AsyncSession = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
) -> list[Turma]:
    matriculas = await matricula_repository.list_ativas_por_aluno(db, usuario.id)
    turmas = []
    for matricula in matriculas:
        turma = await turma_repository.get_by_id(db, matricula.turma_id)
        if turma is not None:
            turmas.append(turma)
    return turmas


@router.get("/me/turmas/{turma_id}/progresso", response_model=ProgressoAlunoResponse)
async def obter_meu_progresso(
    turma_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
) -> ProgressoAlunoResponse:
    matricula = await matricula_repository.get_ativa(db, turma_id=turma_id, aluno_id=usuario.id)
    if matricula is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Voce nao esta matriculado nesta turma.")

    progresso = await progresso_service.obter_progresso_aluno_na_turma(
        db, turma_id=turma_id, aluno=usuario
    )
    return ProgressoAlunoResponse(
        aluno_id=progresso.aluno.id,
        aluno_nome=progresso.aluno.nome,
        problemas_resolvidos=progresso.problemas_resolvidos,
        tentativas=progresso.tentativas,
        tempo_gasto_minutos=progresso.tempo_gasto_minutos,
    )
