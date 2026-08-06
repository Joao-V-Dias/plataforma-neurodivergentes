"""Trilha de auditoria: quem fez o que, quando. Registro append-only (sem
updated_at - um log de auditoria nunca deve ser alterado apos criado), usado
inicialmente para eventos de autenticacao e, a partir da Parte 3+, para
criacao/edicao/exclusao de turmas, alunos e problemas."""

import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import JSON, DateTime, ForeignKey, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, UUIDPrimaryKeyMixin


class AuditLog(Base, UUIDPrimaryKeyMixin):
    __tablename__ = "audit_logs"

    # Nulo em eventos onde o usuario ainda nao foi identificado com certeza
    # (ex: tentativa de login com e-mail que nao existe).
    usuario_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("usuarios.id", ondelete="SET NULL"),
        index=True,
        nullable=True,
    )
    acao: Mapped[str] = mapped_column(String(100), index=True, nullable=False)
    entidade: Mapped[str] = mapped_column(String(100), nullable=False)
    entidade_id: Mapped[str | None] = mapped_column(String(100), nullable=True)
    detalhes: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    ip_address: Mapped[str | None] = mapped_column(String(45), nullable=True)
    criado_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    def __repr__(self) -> str:  # pragma: no cover
        return f"AuditLog(acao={self.acao!r}, usuario_id={self.usuario_id!r})"
