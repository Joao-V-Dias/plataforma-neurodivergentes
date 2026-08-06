"""Dependencias FastAPI reutilizaveis pelos routers: extracao/validacao do
usuario autenticado a partir do JWT (Bearer) e checagem de RBAC."""

from collections.abc import Callable

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.rbac import papeis_a_partir_de
from app.core.security import TokenExpiredError, TokenInvalidError, TokenType, decode_token
from app.models.usuario import Papel, Usuario
from app.repositories import usuario_repository

_bearer_scheme = HTTPBearer(auto_error=False)


def get_client_ip(request: Request) -> str | None:
    return request.client.host if request.client else None


async def get_current_user(
    db: AsyncSession = Depends(get_db),
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer_scheme),
) -> Usuario:
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Nao autenticado.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        claims = decode_token(credentials.credentials, tipo_esperado=TokenType.ACCESS)
    except TokenExpiredError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expirado.",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc
    except TokenInvalidError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token invalido.",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc

    usuario = await usuario_repository.get_by_id(db, claims.usuario_id)
    if usuario is None or not usuario.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario invalido ou inativo.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return usuario


def require_roles(*papeis_permitidos: Papel) -> Callable[[Usuario], Usuario]:
    def dependency(usuario: Usuario = Depends(get_current_user)) -> Usuario:
        if usuario.papel not in papeis_permitidos:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Voce nao tem permissao para acessar este recurso.",
            )
        return usuario

    return dependency


def require_min_role(papel_minimo: Papel) -> Callable[[Usuario], Usuario]:
    return require_roles(*papeis_a_partir_de(papel_minimo))
