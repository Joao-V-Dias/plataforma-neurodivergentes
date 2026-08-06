"""Acesso a dados da tabela `usuarios`. Nenhuma regra de negocio aqui (isso
vive em app/services) - so consultas e persistencia."""

import uuid
from collections.abc import Sequence
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.usuario import Papel, Usuario


async def get_by_id(db: AsyncSession, usuario_id: uuid.UUID) -> Usuario | None:
    return await db.get(Usuario, usuario_id)


async def get_by_email(db: AsyncSession, email: str) -> Usuario | None:
    result = await db.execute(select(Usuario).where(Usuario.email == email.lower()))
    return result.scalar_one_or_none()


async def list_all(db: AsyncSession) -> Sequence[Usuario]:
    result = await db.execute(select(Usuario).order_by(Usuario.nome))
    return result.scalars().all()


async def existe_algum_diretor(db: AsyncSession) -> bool:
    result = await db.execute(select(Usuario.id).where(Usuario.papel == Papel.DIRETOR).limit(1))
    return result.scalar_one_or_none() is not None


async def create(
    db: AsyncSession,
    *,
    nome: str,
    email: str,
    senha_hash: str,
    papel: Papel,
    is_active: bool,
    consentimento_lgpd_aceito_em: datetime | None = None,
    consentimento_lgpd_versao: str | None = None,
) -> Usuario:
    usuario = Usuario(
        nome=nome,
        email=email.lower(),
        senha_hash=senha_hash,
        papel=papel,
        is_active=is_active,
        consentimento_lgpd_aceito_em=consentimento_lgpd_aceito_em,
        consentimento_lgpd_versao=consentimento_lgpd_versao,
    )
    db.add(usuario)
    await db.flush()
    await db.refresh(usuario)
    return usuario


async def atualizar_senha(db: AsyncSession, usuario: Usuario, senha_hash: str) -> None:
    usuario.senha_hash = senha_hash
    db.add(usuario)
    await db.flush()
