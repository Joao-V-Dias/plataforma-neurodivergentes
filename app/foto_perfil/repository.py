"""Acesso a dados da foto de perfil (uma linha por usuario, mutavel
in-place - mesmo padrao de app/repositories/avatar_repository.py)."""

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.foto_perfil.model import FotoPerfil


async def get_by_usuario(db: AsyncSession, usuario_id: uuid.UUID) -> FotoPerfil | None:
    result = await db.execute(select(FotoPerfil).where(FotoPerfil.usuario_id == usuario_id))
    return result.scalar_one_or_none()


async def upsert(
    db: AsyncSession,
    *,
    usuario_id: uuid.UUID,
    nome_arquivo: str,
    content_type: str,
    tamanho_bytes: int,
) -> FotoPerfil:
    foto = await get_by_usuario(db, usuario_id)
    if foto is None:
        foto = FotoPerfil(usuario_id=usuario_id)
        db.add(foto)

    foto.nome_arquivo = nome_arquivo
    foto.content_type = content_type
    foto.tamanho_bytes = tamanho_bytes

    await db.flush()
    await db.refresh(foto)
    return foto


async def excluir(db: AsyncSession, foto: FotoPerfil) -> None:
    await db.delete(foto)
    await db.flush()
