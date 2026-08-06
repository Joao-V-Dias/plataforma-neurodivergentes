"""Registro de trilha de auditoria. Usado por app/services/auth_service.py
desde ja (login, logout, reset de senha) e, a partir da Parte 3+, por
qualquer service que crie/edite/exclua turmas, alunos, problemas etc.

Nunca registre dados sensiveis (senha, token bruto) em `detalhes` - apenas
identificadores e metadados do evento."""

import uuid
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.audit_log import AuditLog


async def registrar_evento(
    db: AsyncSession,
    *,
    acao: str,
    entidade: str,
    usuario_id: uuid.UUID | None = None,
    entidade_id: str | None = None,
    detalhes: dict[str, Any] | None = None,
    ip_address: str | None = None,
) -> None:
    registro = AuditLog(
        usuario_id=usuario_id,
        acao=acao,
        entidade=entidade,
        entidade_id=entidade_id,
        detalhes=detalhes,
        ip_address=ip_address,
    )
    db.add(registro)
    await db.flush()
