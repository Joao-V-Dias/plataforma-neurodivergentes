"""Token de recuperacao de senha, de uso unico e expiracao curta.

Ao contrario do refresh token (que viaja como JWT auto-contido), o token de
reset e um segredo opaco enviado por e-mail: guardamos apenas o hash
(sha256) dele, nunca o valor bruto, para que um vazamento do banco nao
permita a um atacante redefinir senhas de usuarios."""

import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class PasswordResetToken(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "password_reset_tokens"

    usuario_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("usuarios.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    token_hash: Mapped[str] = mapped_column(String(64), unique=True, index=True, nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    used_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    def __repr__(self) -> str:  # pragma: no cover
        return f"PasswordResetToken(usuario_id={self.usuario_id!r}, used_at={self.used_at!r})"
