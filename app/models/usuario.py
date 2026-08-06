"""Modelo de usuario e papel de acesso (RBAC hierarquico).

Os perfis de adaptacao (PerfilAluno, PerfilBigFive) - dados sensiveis de
saude que exigem tratamento e consentimento proprios - vivem em modulos
separados (app/models/perfil_aluno.py, perfil_big_five.py), nunca aqui:
Usuario carrega apenas o consentimento *geral* de cadastro."""

import uuid
from datetime import datetime
from enum import StrEnum

from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class Papel(StrEnum):
    """Papeis de acesso, em ordem hierarquica crescente de privilegio:
    ALUNO < PROFESSOR < COORDENADOR < DIRETOR."""

    DIRETOR = "diretor"
    COORDENADOR = "coordenador"
    PROFESSOR = "professor"
    ALUNO = "aluno"


class Usuario(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "usuarios"

    nome: Mapped[str] = mapped_column(String(200), nullable=False)
    email: Mapped[str] = mapped_column(String(320), unique=True, index=True, nullable=False)
    senha_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    papel: Mapped[Papel] = mapped_column(
        Enum(Papel, name="papel_usuario", native_enum=True), nullable=False
    )

    # Toda a hierarquia de RBAC e escopada por instituicao (multi-tenant).
    instituicao_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("instituicoes.id", ondelete="RESTRICT"),
        index=True,
        nullable=False,
    )

    # Contas criadas por uma autoridade (diretor/coordenador/professor) ja
    # nascem ativas; auto-cadastro de aluno nasce inativo, aguardando
    # aprovacao (POST /usuarios/{id}/aprovar, Parte 3).
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, server_default="true")

    # Consentimento LGPD: dado de saude/perfil psicologico (Parte 3) so pode
    # ser coletado apos consentimento explicito e versionado. Ver docs/lgpd.md.
    consentimento_lgpd_aceito_em: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    consentimento_lgpd_versao: Mapped[str | None] = mapped_column(String(20), nullable=True)

    def __repr__(self) -> str:  # pragma: no cover - apenas debug
        return f"Usuario(id={self.id!r}, email={self.email!r}, papel={self.papel!r})"
