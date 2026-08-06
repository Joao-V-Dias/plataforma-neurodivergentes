"""Acesso a dados da tabela `password_reset_tokens`."""

import uuid
from datetime import UTC, datetime

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.password_reset_token import PasswordResetToken


async def create(
    db: AsyncSession, *, usuario_id: uuid.UUID, token_hash: str, expires_at: datetime
) -> PasswordResetToken:
    token = PasswordResetToken(usuario_id=usuario_id, token_hash=token_hash, expires_at=expires_at)
    db.add(token)
    await db.flush()
    await db.refresh(token)
    return token


async def get_valido_por_hash(db: AsyncSession, token_hash: str) -> PasswordResetToken | None:
    result = await db.execute(
        select(PasswordResetToken).where(
            PasswordResetToken.token_hash == token_hash,
            PasswordResetToken.used_at.is_(None),
            PasswordResetToken.expires_at > datetime.now(UTC),
        )
    )
    return result.scalar_one_or_none()


async def marcar_usado(db: AsyncSession, token: PasswordResetToken) -> None:
    token.used_at = datetime.now(UTC)
    db.add(token)
    await db.flush()


async def invalidar_pendentes_do_usuario(db: AsyncSession, usuario_id: uuid.UUID) -> None:
    await db.execute(
        update(PasswordResetToken)
        .where(
            PasswordResetToken.usuario_id == usuario_id,
            PasswordResetToken.used_at.is_(None),
        )
        .values(used_at=datetime.now(UTC))
    )
