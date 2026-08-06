"""Gestao de usuarios: listagem escopada a instituicao, criacao
hierarquica (Diretor cria Coordenador, Coordenador cria Professor,
Professor cria Aluno - ou qualquer papel estritamente abaixo do criador)
e aprovacao de aluno auto-cadastrado."""

import uuid

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_client_ip, require_min_role
from app.core.database import get_db
from app.models.usuario import Papel, Usuario
from app.repositories import usuario_repository
from app.schemas.auth import UsuarioPublico
from app.schemas.usuarios import CriarUsuarioRequest
from app.services import usuario_service
from app.services.exceptions import (
    EmailJaCadastradoError,
    HierarquiaInvalidaError,
    InstituicaoDiferenteError,
    RecursoNaoEncontradoError,
)

router = APIRouter(prefix="/usuarios", tags=["usuarios"])


@router.get("", response_model=list[UsuarioPublico])
async def listar_usuarios(
    db: AsyncSession = Depends(get_db),
    usuario: Usuario = Depends(require_min_role(Papel.PROFESSOR)),
) -> list[Usuario]:
    """Lista usuarios da mesma instituicao do requisitante (isolamento
    multi-tenant) - CRUD completo com filtros por turma vem na Parte 4."""
    return list(await usuario_repository.list_por_instituicao(db, usuario.instituicao_id))


@router.post("", response_model=UsuarioPublico, status_code=status.HTTP_201_CREATED)
async def criar_usuario(
    payload: CriarUsuarioRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
    criador: Usuario = Depends(require_min_role(Papel.PROFESSOR)),
) -> Usuario:
    try:
        return await usuario_service.criar_usuario_por_hierarquia(
            db,
            criador=criador,
            nome=payload.nome,
            email=payload.email,
            senha=payload.senha,
            papel=payload.papel,
            ip_address=get_client_ip(request),
        )
    except HierarquiaInvalidaError as exc:
        raise HTTPException(status.HTTP_403_FORBIDDEN, str(exc)) from exc
    except EmailJaCadastradoError as exc:
        raise HTTPException(status.HTTP_409_CONFLICT, str(exc)) from exc


@router.get("/{usuario_id}", response_model=UsuarioPublico)
async def obter_usuario(
    usuario_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    requisitante: Usuario = Depends(require_min_role(Papel.PROFESSOR)),
) -> Usuario:
    alvo = await usuario_repository.get_by_id(db, usuario_id)
    if alvo is None or alvo.instituicao_id != requisitante.instituicao_id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Usuario nao encontrado.")
    return alvo


@router.post("/{usuario_id}/aprovar", response_model=UsuarioPublico)
async def aprovar_usuario(
    usuario_id: uuid.UUID,
    request: Request,
    db: AsyncSession = Depends(get_db),
    aprovador: Usuario = Depends(require_min_role(Papel.PROFESSOR)),
) -> Usuario:
    """Ativa um aluno auto-cadastrado (POST /auth/register), completando o
    fluxo 'aluno se autocadastra com aprovacao' do escopo."""
    try:
        return await usuario_service.aprovar_usuario(
            db,
            aprovador=aprovador,
            usuario_id=usuario_id,
            ip_address=get_client_ip(request),
        )
    except RecursoNaoEncontradoError as exc:
        raise HTTPException(status.HTTP_404_NOT_FOUND, str(exc)) from exc
    except InstituicaoDiferenteError as exc:
        raise HTTPException(status.HTTP_403_FORBIDDEN, str(exc)) from exc
