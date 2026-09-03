"""Pontuacao e sequencia de dias ativos (streak) do aluno - estado mutavel
atualizado a cada submissao (app/services/pontuacao_service.py), nunca
escrito diretamente pelo cliente. Uma linha por aluno, mesmo padrao de
PreferenciasAcessibilidade/PerfilJogo."""

import uuid
from datetime import date

from sqlalchemy import Date, ForeignKey, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class Pontuacao(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "pontuacoes"

    aluno_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("usuarios.id", ondelete="CASCADE"),
        unique=True,
        index=True,
        nullable=False,
    )

    pontos: Mapped[int] = mapped_column(Integer, default=0, server_default="0")
    sequencia_dias: Mapped[int] = mapped_column(Integer, default=0, server_default="0")
    maior_sequencia_dias: Mapped[int] = mapped_column(Integer, default=0, server_default="0")
    ultima_atividade_em: Mapped[date | None] = mapped_column(Date, nullable=True)

    def __repr__(self) -> str:  # pragma: no cover
        return f"Pontuacao(aluno_id={self.aluno_id!r}, pontos={self.pontos!r})"
