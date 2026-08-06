"""Refresh tokens emitidos por login/refresh. Guardamos apenas o `jti`
(identificador aleatorio embutido no JWT), nunca o token inteiro - o JWT em
si e auto-contido e assinado, entao o registro aqui serve só para permitir
revogacao/rotacao (algo que um JWT stateless sozinho nao permite)."""

import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class RefreshToken(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "refresh_tokens"

    usuario_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("usuarios.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    jti: Mapped[str] = mapped_column(String(36), unique=True, index=True, nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # Encadeamento de rotacao: aponta para o jti do token que o substituiu,
    # usado para detectar reuso de um refresh token ja rotacionado (sinal
    # de possivel roubo de token) e revogar a sessao inteira.
    substituido_por_jti: Mapped[str | None] = mapped_column(String(36), nullable=True)

    user_agent: Mapped[str | None] = mapped_column(String(300), nullable=True)
    ip_address: Mapped[str | None] = mapped_column(String(45), nullable=True)

    def __repr__(self) -> str:  # pragma: no cover
        return f"RefreshToken(jti={self.jti!r}, usuario_id={self.usuario_id!r})"
