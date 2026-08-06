"""Schemas de request/response do fluxo de autenticacao. A validacao
estrita de input (tamanho, formato de e-mail, forca minima de senha) e
feita aqui pelo Pydantic antes de qualquer dado chegar na camada de
servico - uma das protecoes basicas contra input malicioso exigidas pelo
escopo (OWASP)."""

import uuid
from datetime import datetime

from pydantic import BaseModel, EmailStr, Field, field_validator

from app.models.usuario import Papel
from app.schemas.validators import validar_forca_senha


class RegistroAlunoRequest(BaseModel):
    nome: str = Field(..., min_length=2, max_length=200)
    email: EmailStr
    senha: str = Field(..., min_length=8, max_length=128)
    instituicao_codigo: str = Field(
        ..., min_length=1, max_length=20, description="Codigo da instituicao fornecido pela escola."
    )
    aceite_lgpd: bool = Field(
        ..., description="Consentimento explicito com a politica de tratamento de dados."
    )

    _validar_senha = field_validator("senha")(validar_forca_senha)


class LoginRequest(BaseModel):
    email: EmailStr
    senha: str = Field(..., min_length=1, max_length=128)


class RefreshRequest(BaseModel):
    refresh_token: str


class LogoutRequest(BaseModel):
    refresh_token: str


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ForgotPasswordResponse(BaseModel):
    message: str
    reset_token: str | None = Field(
        default=None,
        description="Presente apenas fora de producao, como substituto de envio por e-mail.",
    )


class ResetPasswordRequest(BaseModel):
    token: str
    nova_senha: str = Field(..., min_length=8, max_length=128)

    _validar_senha = field_validator("nova_senha")(validar_forca_senha)


class TokenResponse(BaseModel):
    access_token: str
    access_token_expires_at: datetime
    refresh_token: str
    refresh_token_expires_at: datetime
    token_type: str = "bearer"


class UsuarioPublico(BaseModel):
    id: uuid.UUID
    nome: str
    email: str
    papel: Papel
    instituicao_id: uuid.UUID
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}
