"""Avatar e apelido escolhidos pelo aluno (personalizacao visual, nao dado
sensivel) - mutavel in-place, uma linha por aluno, mesmo padrao de
PreferenciasAcessibilidade. Reduz ansiedade social e da uma camada de
privacidade a quem prefere nao usar o proprio nome dentro da turma."""

import uuid

from sqlalchemy import ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class PerfilJogo(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "perfis_jogo"

    aluno_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("usuarios.id", ondelete="CASCADE"),
        unique=True,
        index=True,
        nullable=False,
    )

    apelido: Mapped[str | None] = mapped_column(String(40), nullable=True)
    avatar_codigo: Mapped[str | None] = mapped_column(String(30), nullable=True)

    def __repr__(self) -> str:  # pragma: no cover
        return f"PerfilJogo(aluno_id={self.aluno_id!r})"
