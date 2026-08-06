"""Banco de problemas: CRUD de problema com casos de teste, vinculacao a
turma, submissao de codigo (execucao sandboxada) e historico. Casos de
teste ocultos e detalhes do resultado de casos ocultos nunca sao expostos
ao aluno - so passou/falhou."""

import uuid

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import (
    get_client_ip,
    get_current_user,
    get_problema_acessivel,
    get_turma_acessivel_para_membro,
    require_min_role,
    require_roles,
)
from app.core.database import get_db
from app.models.problema import CategoriaTag, Problema
from app.models.submissao import Submissao
from app.models.turma import Turma
from app.models.usuario import Papel, Usuario
from app.repositories import (
    problema_repository,
    submissao_repository,
    tag_repository,
    turma_repository,
)
from app.schemas.problemas import (
    CasoTesteResponse,
    CriarProblemaRequest,
    ProblemaDetalheResponse,
    ProblemaResponse,
    ResultadoCasoResponse,
    SubmeterCodigoRequest,
    SubmissaoResponse,
    SubmissaoResumoResponse,
    TagPublica,
    VincularTurmaRequest,
)
from app.services import problema_service, submissao_service
from app.services.exceptions import (
    InstituicaoDiferenteError,
    LinguagemNaoSuportadaError,
    TagInvalidaError,
)
from app.services.problema_service import CasoTesteInput, ProblemaDetalhado
from app.services.submissao_service import SubmissaoDetalhada

router = APIRouter(tags=["problemas"])


def _problema_response(detalhe: ProblemaDetalhado) -> ProblemaResponse:
    return ProblemaResponse(
        id=detalhe.problema.id,
        instituicao_id=detalhe.problema.instituicao_id,
        titulo=detalhe.problema.titulo,
        enunciado=detalhe.problema.enunciado,
        linguagem=detalhe.problema.linguagem,
        nivel_dificuldade=detalhe.problema.nivel_dificuldade,
        criado_por_id=detalhe.problema.criado_por_id,
        ativo=detalhe.problema.ativo,
        created_at=detalhe.problema.created_at,
        tags=[TagPublica.model_validate(t) for t in detalhe.tags],
    )


def _problema_detalhe_response(
    detalhe: ProblemaDetalhado, *, mostrar_ocultos: bool
) -> ProblemaDetalheResponse:
    casos = detalhe.casos if mostrar_ocultos else [c for c in detalhe.casos if c.publico]
    return ProblemaDetalheResponse(
        **_problema_response(detalhe).model_dump(),
        casos=[
            CasoTesteResponse(
                id=c.id, entrada=c.entrada, saida_esperada=c.saida_esperada,
                publico=c.publico, ordem=c.ordem,
            )
            for c in casos
        ],
    )


def _submissao_response(detalhada: SubmissaoDetalhada) -> SubmissaoResponse:
    resultados = []
    for r in detalhada.resultados:
        caso = detalhada.casos_por_id.get(r.caso_teste_id)
        publico = caso.publico if caso else False
        resultados.append(
            ResultadoCasoResponse(
                caso_teste_id=r.caso_teste_id,
                publico=publico,
                passou=r.passou,
                tempo_execucao_ms=r.tempo_execucao_ms,
                entrada=caso.entrada if publico and caso else None,
                saida_esperada=caso.saida_esperada if publico and caso else None,
                saida_obtida=r.saida_obtida if publico else None,
                erro=r.erro_sanitizado if publico else None,
            )
        )
    return SubmissaoResponse(
        id=detalhada.submissao.id,
        problema_id=detalhada.submissao.problema_id,
        aluno_id=detalhada.submissao.aluno_id,
        status=detalhada.submissao.status,
        tempo_execucao_ms=detalhada.submissao.tempo_execucao_ms,
        criado_em=detalhada.submissao.criado_em,
        resultados=resultados,
    )


@router.get("/tags", response_model=list[TagPublica])
async def listar_tags(
    categoria: CategoriaTag | None = None,
    db: AsyncSession = Depends(get_db),
    _usuario: Usuario = Depends(get_current_user),
) -> list[TagPublica]:
    tags = await tag_repository.list_ativas(db, categoria)
    return [TagPublica.model_validate(t) for t in tags]


@router.post("/problemas", response_model=ProblemaResponse, status_code=status.HTTP_201_CREATED)
async def criar_problema(
    payload: CriarProblemaRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
    criador: Usuario = Depends(require_min_role(Papel.PROFESSOR)),
) -> ProblemaResponse:
    try:
        detalhe = await problema_service.criar_problema(
            db,
            criador=criador,
            titulo=payload.titulo,
            enunciado=payload.enunciado,
            linguagem=payload.linguagem,
            nivel_dificuldade=payload.nivel_dificuldade,
            tags_codigos=payload.tags_codigos,
            casos=[
                CasoTesteInput(
                    entrada=c.entrada, saida_esperada=c.saida_esperada, publico=c.publico
                )
                for c in payload.casos
            ],
            ip_address=get_client_ip(request),
        )
    except LinguagemNaoSuportadaError as exc:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, str(exc)) from exc
    except TagInvalidaError as exc:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_CONTENT, str(exc)) from exc

    return _problema_response(detalhe)


@router.get("/problemas", response_model=list[ProblemaResponse])
async def listar_problemas(
    db: AsyncSession = Depends(get_db),
    usuario: Usuario = Depends(require_min_role(Papel.PROFESSOR)),
) -> list[ProblemaResponse]:
    problemas = await problema_service.listar_problemas_instituicao(db, usuario.instituicao_id)
    respostas = []
    for p in problemas:
        detalhe = await problema_service.obter_detalhe(db, p)
        respostas.append(_problema_response(detalhe))
    return respostas


@router.get("/turmas/{turma_id}/problemas", response_model=list[ProblemaResponse])
async def listar_problemas_da_turma(
    db: AsyncSession = Depends(get_db),
    turma: Turma = Depends(get_turma_acessivel_para_membro),
) -> list[ProblemaResponse]:
    """Complementa GET /problemas (Professor+, instituição inteira): aqui um
    Aluno matriculado também enxerga os problemas vinculados à sua turma -
    sem isto ele nao tem como descobrir quais problemas resolver."""
    problemas = await problema_service.listar_problemas_turma(db, turma.id)
    respostas = []
    for p in problemas:
        detalhe = await problema_service.obter_detalhe(db, p)
        respostas.append(_problema_response(detalhe))
    return respostas


@router.get("/problemas/{problema_id}", response_model=ProblemaDetalheResponse)
async def obter_problema(
    db: AsyncSession = Depends(get_db),
    problema: Problema = Depends(get_problema_acessivel),
    usuario: Usuario = Depends(get_current_user),
) -> ProblemaDetalheResponse:
    detalhe = await problema_service.obter_detalhe(db, problema)
    mostrar_ocultos = usuario.papel != Papel.ALUNO
    return _problema_detalhe_response(detalhe, mostrar_ocultos=mostrar_ocultos)


@router.post("/problemas/{problema_id}/turmas", status_code=status.HTTP_204_NO_CONTENT)
async def vincular_problema_a_turma(
    payload: VincularTurmaRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
    problema: Problema = Depends(get_problema_acessivel),
    ator: Usuario = Depends(require_min_role(Papel.PROFESSOR)),
) -> None:
    turma = await turma_repository.get_by_id(db, payload.turma_id)
    if turma is None or turma.instituicao_id != ator.instituicao_id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Turma nao encontrada.")
    if ator.papel == Papel.PROFESSOR and not await turma_repository.professor_vinculado(
        db, turma.id, ator.id
    ):
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Voce nao tem acesso a esta turma.")

    try:
        await problema_service.vincular_turma(
            db, ator=ator, problema=problema, turma=turma, ip_address=get_client_ip(request)
        )
    except InstituicaoDiferenteError as exc:
        raise HTTPException(status.HTTP_403_FORBIDDEN, str(exc)) from exc


@router.post(
    "/problemas/{problema_id}/submissoes",
    response_model=SubmissaoResponse,
    status_code=status.HTTP_201_CREATED,
)
async def submeter_codigo(
    payload: SubmeterCodigoRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
    problema: Problema = Depends(get_problema_acessivel),
    aluno: Usuario = Depends(require_roles(Papel.ALUNO)),
) -> SubmissaoResponse:
    detalhada = await submissao_service.submeter(
        db,
        aluno=aluno,
        problema=problema,
        codigo_fonte=payload.codigo_fonte,
        ip_address=get_client_ip(request),
    )
    return _submissao_response(detalhada)


@router.get(
    "/problemas/{problema_id}/minhas-submissoes",
    response_model=list[SubmissaoResumoResponse],
)
async def listar_minhas_submissoes(
    db: AsyncSession = Depends(get_db),
    problema: Problema = Depends(get_problema_acessivel),
    aluno: Usuario = Depends(get_current_user),
) -> list[SubmissaoResumoResponse]:
    submissoes = await submissao_repository.list_por_aluno_e_problema(
        db, problema_id=problema.id, aluno_id=aluno.id
    )
    return [
        SubmissaoResumoResponse(
            id=s.id, aluno_id=s.aluno_id, status=s.status,
            tempo_execucao_ms=s.tempo_execucao_ms, criado_em=s.criado_em,
        )
        for s in submissoes
    ]


@router.get("/problemas/{problema_id}/submissoes", response_model=list[SubmissaoResumoResponse])
async def listar_submissoes_do_problema(
    db: AsyncSession = Depends(get_db),
    problema: Problema = Depends(get_problema_acessivel),
    _ator: Usuario = Depends(require_min_role(Papel.PROFESSOR)),
) -> list[SubmissaoResumoResponse]:
    submissoes = await submissao_repository.list_por_problema(db, problema.id)
    return [
        SubmissaoResumoResponse(
            id=s.id, aluno_id=s.aluno_id, status=s.status,
            tempo_execucao_ms=s.tempo_execucao_ms, criado_em=s.criado_em,
        )
        for s in submissoes
    ]


@router.get("/submissoes/{submissao_id}", response_model=SubmissaoResponse)
async def obter_submissao(
    submissao_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
) -> SubmissaoResponse:
    submissao = await submissao_repository.get_by_id(db, submissao_id)
    if submissao is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Submissao nao encontrada.")

    problema = await _carregar_problema_da_submissao(db, submissao)
    e_o_proprio_aluno = usuario.id == submissao.aluno_id
    e_staff_da_instituicao = (
        usuario.papel != Papel.ALUNO and usuario.instituicao_id == problema.instituicao_id
    )
    if not (e_o_proprio_aluno or e_staff_da_instituicao):
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Submissao nao encontrada.")

    detalhada = await submissao_service.obter_detalhada(db, submissao)
    return _submissao_response(detalhada)


async def _carregar_problema_da_submissao(db: AsyncSession, submissao: Submissao) -> Problema:
    problema = await problema_repository.get_by_id(db, submissao.problema_id)
    assert problema is not None  # integridade referencial garante existencia
    return problema
