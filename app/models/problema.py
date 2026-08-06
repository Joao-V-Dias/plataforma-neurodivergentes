"""Banco de problemas de programacao.

`TagProblema` unifica dois conceitos do escopo que sao estruturalmente
identicos (um vocabulario controlado, multi-select por problema): tags de
tema comuns (ex: "loops", "recursao") e os "metadados de dificuldade
adaptativa" - tipo de raciocinio exigido (ex: "logica sequencial",
"abstracao", "memoria de trabalho") que alimentam a IA da Parte 6. O campo
`categoria` distingue os dois usos sem duplicar tabela/logica."""

import uuid
from enum import StrEnum

from sqlalchemy import Boolean, Column, Enum, ForeignKey, Integer, String, Table, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class NivelDificuldade(StrEnum):
    FACIL = "facil"
    MEDIO = "medio"
    DIFICIL = "dificil"


class CategoriaTag(StrEnum):
    TEMA = "tema"
    RACIOCINIO = "raciocinio"


class TagProblema(Base, UUIDPrimaryKeyMixin):
    __tablename__ = "tags_problema"

    categoria: Mapped[CategoriaTag] = mapped_column(
        Enum(CategoriaTag, name="categoria_tag", native_enum=True), nullable=False
    )
    codigo: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    nome: Mapped[str] = mapped_column(String(150), nullable=False)
    descricao: Mapped[str | None] = mapped_column(Text, nullable=True)
    ativo: Mapped[bool] = mapped_column(Boolean, default=True, server_default="true")

    def __repr__(self) -> str:  # pragma: no cover
        return f"TagProblema(codigo={self.codigo!r}, categoria={self.categoria!r})"


problema_tags = Table(
    "problema_tags",
    Base.metadata,
    Column(
        "problema_id", UUID(as_uuid=True), ForeignKey("problemas.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "tag_id", UUID(as_uuid=True), ForeignKey("tags_problema.id", ondelete="RESTRICT"),
        primary_key=True,
    ),
)

problema_turmas = Table(
    "problema_turmas",
    Base.metadata,
    Column(
        "problema_id", UUID(as_uuid=True), ForeignKey("problemas.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "turma_id", UUID(as_uuid=True), ForeignKey("turmas.id", ondelete="CASCADE"),
        primary_key=True,
    ),
)


class Problema(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "problemas"

    instituicao_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("instituicoes.id", ondelete="RESTRICT"),
        index=True,
        nullable=False,
    )
    titulo: Mapped[str] = mapped_column(String(200), nullable=False)
    enunciado: Mapped[str] = mapped_column(Text, nullable=False)
    # Por enquanto so "python" e executavel (app/sandbox/executor.py); o
    # campo e texto livre de proposito, para nao exigir migration quando
    # novas linguagens forem suportadas no executor.
    linguagem: Mapped[str] = mapped_column(String(30), nullable=False)
    nivel_dificuldade: Mapped[NivelDificuldade] = mapped_column(
        Enum(NivelDificuldade, name="nivel_dificuldade", native_enum=True), nullable=False
    )
    criado_por_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("usuarios.id", ondelete="RESTRICT"), nullable=False
    )
    ativo: Mapped[bool] = mapped_column(Boolean, default=True, server_default="true")

    def __repr__(self) -> str:  # pragma: no cover
        return f"Problema(id={self.id!r}, titulo={self.titulo!r})"


class CasoTeste(Base, UUIDPrimaryKeyMixin):
    __tablename__ = "casos_teste"

    problema_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("problemas.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    entrada: Mapped[str] = mapped_column(Text, nullable=False, default="")
    saida_esperada: Mapped[str] = mapped_column(Text, nullable=False)
    # Caso publico: enunciado/feedback mostram entrada+saida ao aluno.
    # Caso oculto: usado so para corrigir, aluno ve apenas passou/falhou.
    publico: Mapped[bool] = mapped_column(Boolean, default=False, server_default="false")
    ordem: Mapped[int] = mapped_column(Integer, default=0, server_default="0")

    def __repr__(self) -> str:  # pragma: no cover
        return f"CasoTeste(problema_id={self.problema_id!r}, publico={self.publico!r})"
