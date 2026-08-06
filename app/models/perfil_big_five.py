"""Perfil de tracos Big Five (OCEAN), calculado a partir do TIPI (Ten-Item
Personality Inventory - Gosling, Rentfrow & Swann, 2003, "A very brief
measure of the Big Five personality domains", Journal of Research in
Personality, 37, 504-528; instrumento de dominio publico). Ver a formula
de calculo e as 10 perguntas em app/services/big_five_service.py.

Versionado do mesmo jeito que PerfilAluno: append-only, vigente = maior
`versao` para o aluno."""

import uuid
from datetime import datetime

from sqlalchemy import JSON, DateTime, Float, ForeignKey, Integer, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, UUIDPrimaryKeyMixin


class PerfilBigFive(Base, UUIDPrimaryKeyMixin):
    __tablename__ = "perfis_big_five"
    __table_args__ = (UniqueConstraint("aluno_id", "versao", name="uq_perfil_big_five_versao"),)

    aluno_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("usuarios.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    versao: Mapped[int] = mapped_column(Integer, nullable=False)

    # Escala 1.0-7.0 (media dos itens do TIPI), fiel a escala original do
    # instrumento - nao normalizamos para 0-100 para nao perder a
    # rastreabilidade com a literatura psicometrica de referencia.
    score_abertura: Mapped[float] = mapped_column(Float, nullable=False)
    score_conscienciosidade: Mapped[float] = mapped_column(Float, nullable=False)
    score_extroversao: Mapped[float] = mapped_column(Float, nullable=False)
    score_amabilidade: Mapped[float] = mapped_column(Float, nullable=False)
    score_neuroticismo: Mapped[float] = mapped_column(Float, nullable=False)

    # As 10 respostas brutas (1-7), guardadas para transparencia/auditoria
    # do calculo - nunca inferimos score sem o dado bruto correspondente.
    respostas_brutas: Mapped[list[int]] = mapped_column(JSON, nullable=False)

    criado_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    def __repr__(self) -> str:  # pragma: no cover
        return f"PerfilBigFive(aluno_id={self.aluno_id!r}, versao={self.versao!r})"
