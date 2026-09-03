"""Avatar/apelido (personalizacao, mutavel pelo proprio aluno), pontuacao
com sequencia de dias ativos e emblemas (ambos calculados a partir de
submissoes - nunca escritos diretamente pelo cliente, ver
app/services/pontuacao_service.py e app/services/emblema_service.py)."""

import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_aluno_acessivel, get_current_user
from app.core.database import get_db
from app.models.pontuacao import Pontuacao
from app.models.usuario import Usuario
from app.repositories import avatar_repository, emblema_repository, pontuacao_repository
from app.schemas.gamificacao import (
    EmblemaConquistadoResponse,
    EmblemaResponse,
    PerfilJogoRequest,
    PerfilJogoResponse,
    PontuacaoResponse,
)

router = APIRouter(tags=["gamificacao"])


def _pontuacao_response(aluno_id: uuid.UUID, pontuacao: Pontuacao | None) -> PontuacaoResponse:
    if pontuacao is None:
        return PontuacaoResponse(
            aluno_id=aluno_id,
            pontos=0,
            sequencia_dias=0,
            maior_sequencia_dias=0,
            ultima_atividade_em=None,
        )
    return PontuacaoResponse.model_validate(pontuacao)


def _emblemas_conquistados_response(
    conquistados: list[tuple],
) -> list[EmblemaConquistadoResponse]:
    return [
        EmblemaConquistadoResponse(
            id=e.id, codigo=e.codigo, nome=e.nome, descricao=e.descricao, conquistado_em=quando
        )
        for e, quando in conquistados
    ]


@router.get("/me/avatar", response_model=PerfilJogoResponse)
async def obter_meu_avatar(
    db: AsyncSession = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
) -> PerfilJogoResponse:
    perfil = await avatar_repository.get_by_aluno(db, usuario.id)
    if perfil is None:
        return PerfilJogoResponse(aluno_id=usuario.id, apelido=None, avatar_codigo=None)
    return PerfilJogoResponse.model_validate(perfil)


@router.put("/me/avatar", response_model=PerfilJogoResponse)
async def atualizar_meu_avatar(
    payload: PerfilJogoRequest,
    db: AsyncSession = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
) -> PerfilJogoResponse:
    perfil = await avatar_repository.upsert(
        db, aluno_id=usuario.id, apelido=payload.apelido, avatar_codigo=payload.avatar_codigo
    )
    return PerfilJogoResponse.model_validate(perfil)


@router.get("/me/pontuacao", response_model=PontuacaoResponse)
async def obter_minha_pontuacao(
    db: AsyncSession = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
) -> PontuacaoResponse:
    pontuacao = await pontuacao_repository.get_by_aluno(db, usuario.id)
    return _pontuacao_response(usuario.id, pontuacao)


@router.get("/alunos/{aluno_id}/pontuacao", response_model=PontuacaoResponse)
async def obter_pontuacao_de_aluno(
    db: AsyncSession = Depends(get_db),
    aluno: Usuario = Depends(get_aluno_acessivel),
) -> PontuacaoResponse:
    pontuacao = await pontuacao_repository.get_by_aluno(db, aluno.id)
    return _pontuacao_response(aluno.id, pontuacao)


@router.get("/emblemas", response_model=list[EmblemaResponse])
async def listar_emblemas(
    db: AsyncSession = Depends(get_db),
    _usuario: Usuario = Depends(get_current_user),
) -> list[EmblemaResponse]:
    emblemas = await emblema_repository.list_ativos(db)
    return [EmblemaResponse.model_validate(e) for e in emblemas]


@router.get("/me/emblemas", response_model=list[EmblemaConquistadoResponse])
async def listar_meus_emblemas(
    db: AsyncSession = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
) -> list[EmblemaConquistadoResponse]:
    conquistados = await emblema_repository.list_conquistados(db, usuario.id)
    return _emblemas_conquistados_response(list(conquistados))


@router.get("/alunos/{aluno_id}/emblemas", response_model=list[EmblemaConquistadoResponse])
async def listar_emblemas_de_aluno(
    db: AsyncSession = Depends(get_db),
    aluno: Usuario = Depends(get_aluno_acessivel),
) -> list[EmblemaConquistadoResponse]:
    conquistados = await emblema_repository.list_conquistados(db, aluno.id)
    return _emblemas_conquistados_response(list(conquistados))
