"""Submissao de codigo de um aluno para um problema, com o resultado por
caso de teste. Cada submissao e imutavel apos concluida (nunca reeditamos
uma tentativa - uma nova tentativa e uma nova linha), preservando o
historico completo exigido pelo escopo."""

import uuid
from datetime import datetime
from enum import StrEnum

from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, Integer, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, UUIDPrimaryKeyMixin


class StatusSubmissao(StrEnum):
    ACEITO = "aceito"
    REPROVADO = "reprovado"
    ERRO_EXECUCAO = "erro_execucao"
    TEMPO_EXCEDIDO = "tempo_excedido"
    ERRO_INTERNO = "erro_interno"


class Submissao(Base, UUIDPrimaryKeyMixin):
    __tablename__ = "submissoes"

    problema_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("problemas.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    aluno_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("usuarios.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    codigo_fonte: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[StatusSubmissao] = mapped_column(
        Enum(StatusSubmissao, name="status_submissao", native_enum=True), nullable=False
    )
    tempo_execucao_ms: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    criado_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    def __repr__(self) -> str:  # pragma: no cover
        return f"Submissao(id={self.id!r}, status={self.status!r})"


class SubmissaoResultado(Base, UUIDPrimaryKeyMixin):
    __tablename__ = "submissao_resultados"

    submissao_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("submissoes.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    caso_teste_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("casos_teste.id", ondelete="CASCADE"), nullable=False
    )
    passou: Mapped[bool] = mapped_column(Boolean, nullable=False)
    # Guardado sempre (para o professor auditar), mas so exposto na API
    # quando o caso de teste correspondente e publico - ver
    # app/services/submissao_service.py.
    saida_obtida: Mapped[str] = mapped_column(Text, nullable=False, default="")
    erro_sanitizado: Mapped[str | None] = mapped_column(Text, nullable=True)
    tempo_execucao_ms: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    def __repr__(self) -> str:  # pragma: no cover
        return f"SubmissaoResultado(submissao_id={self.submissao_id!r}, passou={self.passou!r})"
