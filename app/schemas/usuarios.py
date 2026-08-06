"""Schemas de gestao de usuarios (criacao hierarquica e aprovacao)."""

from pydantic import BaseModel, EmailStr, Field, field_validator

from app.models.usuario import Papel
from app.schemas.validators import validar_forca_senha


class CriarUsuarioRequest(BaseModel):
    nome: str = Field(..., min_length=2, max_length=200)
    email: EmailStr
    senha: str = Field(..., min_length=8, max_length=128)
    papel: Papel

    _validar_senha = field_validator("senha")(validar_forca_senha)
