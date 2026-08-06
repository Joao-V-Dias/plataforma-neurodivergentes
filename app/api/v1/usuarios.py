"""Listagem minima de usuarios, usada por enquanto so para comprovar o RBAC
hierarquico (Diretor/Coordenador/Professor podem ver; Aluno nao pode). O
CRUD completo, com filtros por instituicao/turma e regras de visibilidade
detalhadas, e entregue na Parte 3."""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import require_min_role
from app.core.database import get_db
from app.models.usuario import Papel, Usuario
from app.repositories import usuario_repository
from app.schemas.auth import UsuarioPublico

router = APIRouter(prefix="/usuarios", tags=["usuarios"])


@router.get("", response_model=list[UsuarioPublico])
async def listar_usuarios(
    db: AsyncSession = Depends(get_db),
    _usuario: Usuario = Depends(require_min_role(Papel.PROFESSOR)),
) -> list[Usuario]:
    return list(await usuario_repository.list_all(db))
