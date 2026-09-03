"""Endpoints de upload/consulta/remocao da foto de perfil e de servico do
arquivo (autenticado - a foto nao e publica na internet, so dentro da
plataforma logada)."""

import uuid

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.core.database import get_db
from app.foto_perfil import storage
from app.foto_perfil.repository import excluir, get_by_usuario, upsert
from app.foto_perfil.schemas import FotoPerfilResponse
from app.models.usuario import Usuario

router = APIRouter(tags=["foto-perfil"])


def _url(usuario_id: uuid.UUID) -> str:
    return f"/api/v1/usuarios/{usuario_id}/foto/arquivo"


@router.get("/me/foto", response_model=FotoPerfilResponse)
async def obter_minha_foto(
    db: AsyncSession = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
) -> FotoPerfilResponse:
    foto = await get_by_usuario(db, usuario.id)
    if foto is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Sem foto de perfil.")
    return FotoPerfilResponse(usuario_id=usuario.id, url=_url(usuario.id))


@router.put("/me/foto", response_model=FotoPerfilResponse)
async def enviar_minha_foto(
    arquivo: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
) -> FotoPerfilResponse:
    nome_arquivo, content_type, tamanho_bytes = await storage.salvar(usuario.id, arquivo)
    await upsert(
        db,
        usuario_id=usuario.id,
        nome_arquivo=nome_arquivo,
        content_type=content_type,
        tamanho_bytes=tamanho_bytes,
    )
    return FotoPerfilResponse(usuario_id=usuario.id, url=_url(usuario.id))


@router.delete("/me/foto", status_code=status.HTTP_204_NO_CONTENT)
async def remover_minha_foto(
    db: AsyncSession = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
) -> None:
    foto = await get_by_usuario(db, usuario.id)
    if foto is not None:
        await excluir(db, foto)
    storage.remover(usuario.id)


@router.get("/usuarios/{usuario_id}/foto/arquivo")
async def obter_arquivo_foto(
    usuario_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _usuario: Usuario = Depends(get_current_user),
) -> FileResponse:
    """Qualquer usuario autenticado pode ver a foto de outro (e uma foto de
    perfil dentro da plataforma, como o avatar de icone hoje) - restringir
    por instituicao/turma como get_aluno_acessivel faz seria pouco util
    aqui, ja que colegas de turma tambem precisam ver a foto uns dos
    outros."""
    foto = await get_by_usuario(db, usuario_id)
    if foto is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Sem foto de perfil.")
    caminho = storage.caminho_arquivo(foto.nome_arquivo)
    if not caminho.exists():
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Arquivo nao encontrado.")
    return FileResponse(caminho, media_type=foto.content_type)
