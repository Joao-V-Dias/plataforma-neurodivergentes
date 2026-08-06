"""Preferencias de acessibilidade: configuracao de UI, nao dado clinico.
Ao contrario de PerfilAluno/PerfilBigFive, isto e mutavel in-place (nao
versionado) - e so uma preferencia de exibicao, sem valor de historico
clinico, e qualquer usuario (nao so aluno) pode ter as suas."""

import uuid

from sqlalchemy import Boolean, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class PreferenciasAcessibilidade(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "preferencias_acessibilidade"

    usuario_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("usuarios.id", ondelete="CASCADE"),
        unique=True,
        index=True,
        nullable=False,
    )

    fonte_legivel: Mapped[bool] = mapped_column(Boolean, default=False, server_default="false")
    alto_contraste: Mapped[bool] = mapped_column(Boolean, default=False, server_default="false")
    tempo_extra_percentual: Mapped[int] = mapped_column(Integer, default=0, server_default="0")
    leitura_voz_alta: Mapped[bool] = mapped_column(Boolean, default=False, server_default="false")
    reducao_estimulos: Mapped[bool] = mapped_column(Boolean, default=False, server_default="false")
    tamanho_fonte: Mapped[str] = mapped_column(String(10), default="medio", server_default="medio")

    def __repr__(self) -> str:  # pragma: no cover
        return f"PreferenciasAcessibilidade(usuario_id={self.usuario_id!r})"
