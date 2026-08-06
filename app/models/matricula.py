"""Matricula de aluno em turma. Nao apagamos nem sobrescrevemos ao
desmatricular - marcamos `ativo=False` e preenchemos `desmatriculado_em`,
preservando o historico (quem esteve em qual turma e quando)."""

import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class Matricula(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "matriculas"

    turma_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("turmas.id", ondelete="CASCADE"), index=True, nullable=False
    )
    aluno_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("usuarios.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    matriculado_por_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("usuarios.id", ondelete="RESTRICT"), nullable=False
    )

    ativo: Mapped[bool] = mapped_column(Boolean, default=True, server_default="true")
    matriculado_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    desmatriculado_em: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    def __repr__(self) -> str:  # pragma: no cover
        return f"Matricula(turma_id={self.turma_id!r}, aluno_id={self.aluno_id!r})"
