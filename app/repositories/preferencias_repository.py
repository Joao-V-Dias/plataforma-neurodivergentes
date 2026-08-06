"""Acesso a dados de preferencias de acessibilidade (uma linha por
usuario, mutavel in-place - nao e dado versionado/clinico)."""

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.preferencias_acessibilidade import PreferenciasAcessibilidade


async def get_by_usuario(
    db: AsyncSession, usuario_id: uuid.UUID
) -> PreferenciasAcessibilidade | None:
    result = await db.execute(
        select(PreferenciasAcessibilidade).where(
            PreferenciasAcessibilidade.usuario_id == usuario_id
        )
    )
    return result.scalar_one_or_none()


async def upsert(
    db: AsyncSession,
    *,
    usuario_id: uuid.UUID,
    fonte_legivel: bool,
    alto_contraste: bool,
    tempo_extra_percentual: int,
    leitura_voz_alta: bool,
    reducao_estimulos: bool,
    tamanho_fonte: str,
) -> PreferenciasAcessibilidade:
    preferencias = await get_by_usuario(db, usuario_id)
    if preferencias is None:
        preferencias = PreferenciasAcessibilidade(usuario_id=usuario_id)
        db.add(preferencias)

    preferencias.fonte_legivel = fonte_legivel
    preferencias.alto_contraste = alto_contraste
    preferencias.tempo_extra_percentual = tempo_extra_percentual
    preferencias.leitura_voz_alta = leitura_voz_alta
    preferencias.reducao_estimulos = reducao_estimulos
    preferencias.tamanho_fonte = tamanho_fonte

    await db.flush()
    await db.refresh(preferencias)
    return preferencias
