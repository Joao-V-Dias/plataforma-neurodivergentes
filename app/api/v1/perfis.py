"""Perfis de adaptacao: condicoes de neurodivergencia, questionario e
perfil Big Five, e preferencias de acessibilidade.

Regra de visibilidade (docs/lgpd.md secao 7): o proprio aluno sempre
acessa seu perfil; Professor/Coordenador/Diretor da mesma instituicao
tambem acessam (necessidade legitima pedagogica) - ver
app/api/deps.py:get_aluno_acessivel. Escopo por turma especifica fica
para a Parte 4, quando turmas existirem."""

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_aluno_acessivel, get_client_ip, get_current_user
from app.core.database import get_db
from app.models.perfil_big_five import PerfilBigFive
from app.models.usuario import Usuario
from app.repositories import (
    condicao_repository,
    perfil_big_five_repository,
    preferencias_repository,
)
from app.schemas.perfis import (
    BigFiveRespostasRequest,
    BigFiveScores,
    CondicaoPublica,
    PerfilAlunoResponse,
    PerfilBigFiveResponse,
    PreferenciasAcessibilidadeRequest,
    PreferenciasAcessibilidadeResponse,
    QuestaoTIPI,
    RegistrarPerfilAlunoRequest,
)
from app.services import big_five_service, perfil_aluno_service
from app.services.big_five_service import INSTRUMENTO_REF, QUESTOES_TIPI
from app.services.exceptions import (
    AlvoInvalidoError,
    CondicaoInvalidaError,
    ConsentimentoNaoAceitoError,
)
from app.services.perfil_aluno_service import PerfilAlunoDetalhado

router = APIRouter(tags=["perfis"])


def _perfil_aluno_response(detalhado: PerfilAlunoDetalhado) -> PerfilAlunoResponse:
    return PerfilAlunoResponse(
        id=detalhado.perfil.id,
        aluno_id=detalhado.perfil.aluno_id,
        versao=detalhado.perfil.versao,
        observacoes=detalhado.perfil.observacoes,
        criado_por_id=detalhado.perfil.criado_por_id,
        criado_em=detalhado.perfil.criado_em,
        condicoes=[CondicaoPublica.model_validate(c) for c in detalhado.condicoes],
    )


@router.get("/condicoes-neurodivergencia", response_model=list[CondicaoPublica])
async def listar_condicoes(
    db: AsyncSession = Depends(get_db),
    _usuario: Usuario = Depends(get_current_user),
) -> list[CondicaoPublica]:
    condicoes = await condicao_repository.list_ativas(db)
    return [CondicaoPublica.model_validate(c) for c in condicoes]


@router.get("/big-five/questionario", response_model=list[QuestaoTIPI])
async def obter_questionario_big_five(
    _usuario: Usuario = Depends(get_current_user),
) -> list[QuestaoTIPI]:
    return [QuestaoTIPI(ordem=item.ordem, texto=item.texto) for item in QUESTOES_TIPI]


@router.post(
    "/alunos/{aluno_id}/perfil",
    response_model=PerfilAlunoResponse,
    status_code=status.HTTP_201_CREATED,
)
async def registrar_perfil_aluno(
    payload: RegistrarPerfilAlunoRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
    aluno: Usuario = Depends(get_aluno_acessivel),
    ator: Usuario = Depends(get_current_user),
) -> PerfilAlunoResponse:
    try:
        detalhado = await perfil_aluno_service.registrar_perfil(
            db,
            aluno=aluno,
            criado_por=ator,
            condicoes_codigos=payload.condicoes_codigos,
            observacoes=payload.observacoes,
            aceite_consentimento=payload.aceite_consentimento,
            ip_address=get_client_ip(request),
        )
    except ConsentimentoNaoAceitoError as exc:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, str(exc)) from exc
    except CondicaoInvalidaError as exc:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_CONTENT, str(exc)) from exc
    except AlvoInvalidoError as exc:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, str(exc)) from exc

    return _perfil_aluno_response(detalhado)


@router.get("/alunos/{aluno_id}/perfil", response_model=PerfilAlunoResponse)
async def obter_perfil_aluno_vigente(
    db: AsyncSession = Depends(get_db),
    aluno: Usuario = Depends(get_aluno_acessivel),
) -> PerfilAlunoResponse:
    detalhado = await perfil_aluno_service.obter_vigente(db, aluno.id)
    if detalhado is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Aluno ainda nao tem perfil registrado.")
    return _perfil_aluno_response(detalhado)


@router.get("/alunos/{aluno_id}/perfil/historico", response_model=list[PerfilAlunoResponse])
async def obter_historico_perfil_aluno(
    db: AsyncSession = Depends(get_db),
    aluno: Usuario = Depends(get_aluno_acessivel),
) -> list[PerfilAlunoResponse]:
    historico = await perfil_aluno_service.obter_historico(db, aluno.id)
    return [_perfil_aluno_response(d) for d in historico]


def _perfil_big_five_response(perfil: PerfilBigFive) -> PerfilBigFiveResponse:
    return PerfilBigFiveResponse(
        id=perfil.id,
        aluno_id=perfil.aluno_id,
        versao=perfil.versao,
        criado_em=perfil.criado_em,
        instrumento=INSTRUMENTO_REF,
        scores=BigFiveScores(
            abertura=perfil.score_abertura,
            conscienciosidade=perfil.score_conscienciosidade,
            extroversao=perfil.score_extroversao,
            amabilidade=perfil.score_amabilidade,
            neuroticismo=perfil.score_neuroticismo,
        ),
    )


@router.post(
    "/me/big-five", response_model=PerfilBigFiveResponse, status_code=status.HTTP_201_CREATED
)
async def registrar_meu_big_five(
    payload: BigFiveRespostasRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
) -> PerfilBigFiveResponse:
    try:
        perfil = await big_five_service.registrar_respostas(
            db,
            aluno=usuario,
            respostas=payload.respostas,
            ip_address=get_client_ip(request),
        )
    except AlvoInvalidoError as exc:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, str(exc)) from exc

    return _perfil_big_five_response(perfil)


@router.get("/alunos/{aluno_id}/big-five", response_model=PerfilBigFiveResponse)
async def obter_big_five_vigente(
    db: AsyncSession = Depends(get_db),
    aluno: Usuario = Depends(get_aluno_acessivel),
) -> PerfilBigFiveResponse:
    perfil = await perfil_big_five_repository.get_vigente(db, aluno.id)
    if perfil is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Aluno ainda nao respondeu o Big Five.")
    return _perfil_big_five_response(perfil)


@router.get("/me/preferencias-acessibilidade", response_model=PreferenciasAcessibilidadeResponse)
async def obter_minhas_preferencias(
    db: AsyncSession = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
) -> PreferenciasAcessibilidadeResponse:
    preferencias = await preferencias_repository.get_by_usuario(db, usuario.id)
    if preferencias is None:
        return PreferenciasAcessibilidadeResponse(usuario_id=usuario.id)
    return PreferenciasAcessibilidadeResponse.model_validate(preferencias)


@router.put("/me/preferencias-acessibilidade", response_model=PreferenciasAcessibilidadeResponse)
async def atualizar_minhas_preferencias(
    payload: PreferenciasAcessibilidadeRequest,
    db: AsyncSession = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
) -> PreferenciasAcessibilidadeResponse:
    preferencias = await preferencias_repository.upsert(
        db,
        usuario_id=usuario.id,
        **payload.model_dump(),
    )
    return PreferenciasAcessibilidadeResponse.model_validate(preferencias)
