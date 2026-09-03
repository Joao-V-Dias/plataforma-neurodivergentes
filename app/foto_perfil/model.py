"""Metadados da foto de perfil enviada pelo usuario (o arquivo em si vive
em disco, ver app/foto_perfil/storage.py - a tabela so referencia o nome).
Uma linha por usuario, mutavel in-place, mesmo padrao de PerfilJogo em
app/models/avatar.py."""

import uuid

from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class FotoPerfil(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "fotos_perfil"

    usuario_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("usuarios.id", ondelete="CASCADE"),
        unique=True,
        index=True,
        nullable=False,
    )
    nome_arquivo: Mapped[str] = mapped_column(String(80), nullable=False)
    content_type: Mapped[str] = mapped_column(String(50), nullable=False)
    tamanho_bytes: Mapped[int] = mapped_column(Integer, nullable=False)

    def __repr__(self) -> str:  # pragma: no cover
        return f"FotoPerfil(usuario_id={self.usuario_id!r})"
