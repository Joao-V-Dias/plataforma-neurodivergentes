"""Acesso a dados da tabela `refresh_tokens`."""

import uuid
from datetime import UTC, datetime

from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.refresh_token import RefreshToken


async def create(
    db: AsyncSession,
    *,
    usuario_id: uuid.UUID,
    jti: str,
    expires_at: datetime,
    user_agent: str | None,
    ip_address: str | None,
) -> RefreshToken:
    token = RefreshToken(
        usuario_id=usuario_id,
        jti=jti,
        expires_at=expires_at,
        user_agent=user_agent,
        ip_address=ip_address,
    )
    db.add(token)
    await db.flush()
    await db.refresh(token)
    return token


async def get_by_jti(db: AsyncSession, jti: str) -> RefreshToken | None:
    result = await db.execute(select(RefreshToken).where(RefreshToken.jti == jti))
    return result.scalar_one_or_none()


async def revogar(
    db: AsyncSession, token: RefreshToken, *, substituido_por_jti: str | None = None
) -> None:
    token.revoked_at = datetime.now(UTC)
    if substituido_por_jti is not None:
        token.substituido_por_jti = substituido_por_jti
    db.add(token)
    await db.flush()


async def revogar_todos_do_usuario(db: AsyncSession, usuario_id: uuid.UUID) -> None:
    await db.execute(
        update(RefreshToken)
        .where(RefreshToken.usuario_id == usuario_id, RefreshToken.revoked_at.is_(None))
        .values(revoked_at=func.now())
    )
