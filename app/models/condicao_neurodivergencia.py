"""Vocabulario controlado de condicoes de neurodivergencia (TDAH, TEA,
dislexia, discalculia etc.). Modelado como tabela (nao como enum Python)
de proposito: a lista precisa poder crescer sem exigir uma migration de
schema a cada nova condicao adicionada - so um INSERT."""

from sqlalchemy import Boolean, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class CondicaoNeurodivergencia(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "condicoes_neurodivergencia"

    codigo: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    nome: Mapped[str] = mapped_column(String(150), nullable=False)
    descricao: Mapped[str | None] = mapped_column(Text, nullable=True)
    ativo: Mapped[bool] = mapped_column(Boolean, default=True, server_default="true")

    def __repr__(self) -> str:  # pragma: no cover
        return f"CondicaoNeurodivergencia(codigo={self.codigo!r})"
