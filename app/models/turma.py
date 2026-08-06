"""Turma: unidade operacional do dia a dia de professores e coordenadores.
`professor_responsavel_id` e o titular da turma; `turma_professores` guarda
o conjunto completo de professores com acesso a ela (o titular e adicionado
automaticamente no momento da criacao, mais quem for adicionado depois via
co-docencia)."""

import uuid

from sqlalchemy import Boolean, Column, ForeignKey, String, Table
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin

turma_professores = Table(
    "turma_professores",
    Base.metadata,
    Column(
        "turma_id", UUID(as_uuid=True), ForeignKey("turmas.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "professor_id", UUID(as_uuid=True), ForeignKey("usuarios.id", ondelete="CASCADE"),
        primary_key=True,
    ),
)


class Turma(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "turmas"

    instituicao_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("instituicoes.id", ondelete="RESTRICT"),
        index=True,
        nullable=False,
    )
    nome: Mapped[str] = mapped_column(String(200), nullable=False)
    # Ex: "2026.1" - texto livre de proposito, cada instituicao organiza o
    # calendario a sua maneira (semestral, trimestral, anual etc.).
    periodo: Mapped[str] = mapped_column(String(50), nullable=False)

    professor_responsavel_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("usuarios.id", ondelete="RESTRICT"),
        index=True,
        nullable=False,
    )

    ativo: Mapped[bool] = mapped_column(Boolean, default=True, server_default="true")

    def __repr__(self) -> str:  # pragma: no cover
        return f"Turma(id={self.id!r}, nome={self.nome!r}, periodo={self.periodo!r})"
