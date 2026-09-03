"""Catalogo de emblemas (conquistas) e o registro de quais alunos ja
conquistaram quais - mesmo padrao de TagProblema/CondicaoNeurodivergencia
para o catalogo (vocabulario controlado, extensivel via INSERT) e de
perfil_aluno_condicoes para a associacao, com uma coluna extra
(`conquistado_em`) porque aqui a associacao carrega dado proprio."""

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, String, Table, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class Emblema(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "emblemas"

    codigo: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    nome: Mapped[str] = mapped_column(String(150), nullable=False)
    descricao: Mapped[str | None] = mapped_column(Text, nullable=True)
    ativo: Mapped[bool] = mapped_column(Boolean, default=True, server_default="true")

    def __repr__(self) -> str:  # pragma: no cover
        return f"Emblema(codigo={self.codigo!r})"


# Core Table (nao classe ORM) porque o unico uso e insert/select simples,
# mas precisa de uma coluna alem das duas chaves estrangeiras
# (`conquistado_em`) - por isso nao e so um par de FKs como
# perfil_aluno_condicoes.
aluno_emblemas = Table(
    "aluno_emblemas",
    Base.metadata,
    Column(
        "aluno_id",
        UUID(as_uuid=True),
        ForeignKey("usuarios.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "emblema_id",
        UUID(as_uuid=True),
        ForeignKey("emblemas.id", ondelete="RESTRICT"),
        primary_key=True,
    ),
    Column("conquistado_em", DateTime(timezone=True), server_default=func.now(), nullable=False),
)
