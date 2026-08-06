"""Instituicao de ensino: tenant que agrupa usuarios, turmas e problemas.
Toda hierarquia de RBAC (Diretor > Coordenador > Professor > Aluno) e
escopada a uma unica instituicao - um Diretor nao enxerga nem administra
usuarios de outra instituicao."""

from sqlalchemy import Boolean, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class Instituicao(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "instituicoes"

    nome: Mapped[str] = mapped_column(String(200), nullable=False)

    # Codigo curto e unico usado no auto-cadastro de aluno (a pessoa
    # informa o codigo da escola em vez de escolher de uma lista publica
    # de instituicoes, o que vazaria quais escolas usam a plataforma).
    codigo: Mapped[str] = mapped_column(String(20), unique=True, index=True, nullable=False)

    ativo: Mapped[bool] = mapped_column(Boolean, default=True, server_default="true")

    def __repr__(self) -> str:  # pragma: no cover
        return f"Instituicao(id={self.id!r}, nome={self.nome!r}, codigo={self.codigo!r})"
