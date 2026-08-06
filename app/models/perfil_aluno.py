"""Perfil de neurodivergencia do aluno - dado sensivel de saude (LGPD
Art. 5, II; ver docs/lgpd.md). Versionado de forma append-only: nunca
fazemos UPDATE numa linha existente, sempre inserimos uma nova com
`versao` maior. A versao "vigente" e simplesmente a de maior `versao`
para aquele aluno - sem necessidade de uma flag mutavel, o que elimina
qualquer risco de historico ser reescrito."""

import uuid
from datetime import datetime

from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Table,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, UUIDPrimaryKeyMixin

# Tabela de associacao (Core Table, nao classe ORM) porque nao precisamos
# de nenhum atributo alem das duas chaves estrangeiras.
perfil_aluno_condicoes = Table(
    "perfil_aluno_condicoes",
    Base.metadata,
    Column(
        "perfil_aluno_id",
        UUID(as_uuid=True),
        ForeignKey("perfis_aluno.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "condicao_id",
        UUID(as_uuid=True),
        ForeignKey("condicoes_neurodivergencia.id", ondelete="RESTRICT"),
        primary_key=True,
    ),
)


class PerfilAluno(Base, UUIDPrimaryKeyMixin):
    __tablename__ = "perfis_aluno"
    __table_args__ = (UniqueConstraint("aluno_id", "versao", name="uq_perfil_aluno_versao"),)

    aluno_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("usuarios.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    versao: Mapped[int] = mapped_column(Integer, nullable=False)
    observacoes: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Quem registrou esta versao: o proprio aluno ou um profissional
    # (professor/coordenador/diretor) com base em documentacao apresentada.
    criado_por_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("usuarios.id", ondelete="RESTRICT"), nullable=False
    )

    # Consentimento especifico para este dado sensivel - separado do
    # consentimento geral de cadastro (Usuario.consentimento_lgpd_*).
    # Ver docs/lgpd.md, secao 2.
    consentimento_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    consentimento_versao: Mapped[str] = mapped_column(String(20), nullable=False)

    criado_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    def __repr__(self) -> str:  # pragma: no cover
        return f"PerfilAluno(aluno_id={self.aluno_id!r}, versao={self.versao!r})"
