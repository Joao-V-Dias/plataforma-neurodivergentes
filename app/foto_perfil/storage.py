"""Armazenamento em disco das fotos de perfil: validacao de tipo/tamanho e
gravacao/remocao dos arquivos, isolado do resto do modulo para poder virar
um storage externo (S3 etc.) no futuro sem tocar em repository/router.

Toda imagem enviada e revalidada e regravada pelo Pillow (nunca os bytes
crus do upload) - isso descarta metadados EXIF automaticamente, o que
inclui geolocalizacao de onde a foto foi tirada. Como o publico da
plataforma inclui criancas/adolescentes, isso nao e um detalhe: evita que
uma foto de perfil vaze, sem querer, o endereco de casa do aluno."""

import uuid
from io import BytesIO
from pathlib import Path

from fastapi import HTTPException, UploadFile, status
from PIL import Image, UnidentifiedImageError

CONTENT_TYPES_PERMITIDOS = {"image/jpeg", "image/png", "image/webp"}
TAMANHO_MAXIMO_BYTES = 5 * 1024 * 1024  # 5 MB
LADO_MAXIMO_PX = 1024  # reduz fotos muito grandes; suficiente para um avatar

DIRETORIO_BASE = Path("uploads") / "fotos_perfil"


def _caminho_para(usuario_id: uuid.UUID) -> Path:
    return DIRETORIO_BASE / f"{usuario_id}.jpg"


async def salvar(usuario_id: uuid.UUID, arquivo: UploadFile) -> tuple[str, str, int]:
    """Valida e grava a foto em disco (sempre como JPEG re-codificado),
    substituindo qualquer foto anterior do usuario. Retorna
    (nome_arquivo, content_type, tamanho_bytes) para persistir no banco."""
    if arquivo.content_type not in CONTENT_TYPES_PERMITIDOS:
        raise HTTPException(
            status.HTTP_422_UNPROCESSABLE_ENTITY,
            "Formato de imagem nao suportado (use JPEG, PNG ou WebP).",
        )

    conteudo = await arquivo.read()
    if not conteudo:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, "Arquivo vazio.")
    if len(conteudo) > TAMANHO_MAXIMO_BYTES:
        raise HTTPException(
            status.HTTP_422_UNPROCESSABLE_ENTITY, "Imagem maior que o limite de 5 MB."
        )

    try:
        imagem = Image.open(BytesIO(conteudo))
        imagem.load()
    except UnidentifiedImageError as exc:
        raise HTTPException(
            status.HTTP_422_UNPROCESSABLE_ENTITY, "Arquivo nao e uma imagem valida."
        ) from exc

    imagem = imagem.convert("RGB")
    imagem.thumbnail((LADO_MAXIMO_PX, LADO_MAXIMO_PX))

    DIRETORIO_BASE.mkdir(parents=True, exist_ok=True)
    caminho = _caminho_para(usuario_id)
    imagem.save(caminho, format="JPEG", quality=85)

    return caminho.name, "image/jpeg", caminho.stat().st_size


def remover(usuario_id: uuid.UUID) -> None:
    _caminho_para(usuario_id).unlink(missing_ok=True)


def caminho_arquivo(nome_arquivo: str) -> Path:
    return DIRETORIO_BASE / nome_arquivo
