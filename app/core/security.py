"""Primitivas de seguranca: hash de senha (Argon2id) e JWT de acesso/
refresh. Nenhuma logica de negocio (consultas ao banco, regras de quem pode
fazer o que) mora aqui - so criptografia e codificacao de token."""

import hashlib
import secrets
import uuid
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from enum import StrEnum
from typing import Any

import jwt
from argon2 import PasswordHasher
from argon2.exceptions import Argon2Error

from app.core.config import get_settings
from app.models.usuario import Papel

# Argon2id (padrao da biblioteca) e a recomendacao atual da OWASP para hash
# de senha, preferivel a bcrypt para novas aplicacoes.
_password_hasher = PasswordHasher()


def hash_password(senha_plana: str) -> str:
    return _password_hasher.hash(senha_plana)


def verify_password(senha_plana: str, senha_hash: str) -> bool:
    try:
        return _password_hasher.verify(senha_hash, senha_plana)
    except Argon2Error:
        return False


def password_hash_precisa_atualizar(senha_hash: str) -> bool:
    """Verifica se o hash foi gerado com parametros antigos (ex: apos
    aumentarmos o custo do Argon2) e deveria ser regravado no proximo login
    bem-sucedido."""
    return _password_hasher.check_needs_rehash(senha_hash)


class TokenType(StrEnum):
    ACCESS = "access"
    REFRESH = "refresh"


class TokenError(Exception):
    """Base para erros de token JWT invalido/expirado/tipo incorreto."""


class TokenExpiredError(TokenError):
    pass


class TokenInvalidError(TokenError):
    pass


@dataclass(frozen=True)
class TokenClaims:
    usuario_id: uuid.UUID
    papel: Papel
    tipo: TokenType
    jti: str
    expires_at: datetime


def _encode(
    usuario_id: uuid.UUID, papel: Papel, tipo: TokenType, expires_delta: timedelta
) -> tuple[str, str, datetime]:
    settings = get_settings()
    now = datetime.now(UTC)
    expires_at = now + expires_delta
    jti = str(uuid.uuid4())

    payload = {
        "sub": str(usuario_id),
        "papel": papel.value,
        "type": tipo.value,
        "jti": jti,
        "iat": now,
        "exp": expires_at,
    }
    token = jwt.encode(payload, settings.secret_key, algorithm=settings.jwt_algorithm)
    return token, jti, expires_at


def create_access_token(usuario_id: uuid.UUID, papel: Papel) -> tuple[str, datetime]:
    settings = get_settings()
    token, _jti, expires_at = _encode(
        usuario_id,
        papel,
        TokenType.ACCESS,
        timedelta(minutes=settings.access_token_expire_minutes),
    )
    return token, expires_at


def create_refresh_token(usuario_id: uuid.UUID, papel: Papel) -> tuple[str, str, datetime]:
    """Retorna (token, jti, expires_at). O chamador e responsavel por
    persistir o jti (app/repositories/refresh_token_repository.py) para que
    o token possa ser revogado/rotacionado."""
    settings = get_settings()
    return _encode(
        usuario_id,
        papel,
        TokenType.REFRESH,
        timedelta(days=settings.refresh_token_expire_days),
    )


def decode_token(token: str, *, tipo_esperado: TokenType) -> TokenClaims:
    settings = get_settings()
    try:
        payload: dict[str, Any] = jwt.decode(
            token, settings.secret_key, algorithms=[settings.jwt_algorithm]
        )
    except jwt.ExpiredSignatureError as exc:
        raise TokenExpiredError("Token expirado.") from exc
    except jwt.InvalidTokenError as exc:
        raise TokenInvalidError("Token invalido.") from exc

    if payload.get("type") != tipo_esperado.value:
        raise TokenInvalidError(f"Esperado token do tipo '{tipo_esperado.value}'.")

    try:
        return TokenClaims(
            usuario_id=uuid.UUID(payload["sub"]),
            papel=Papel(payload["papel"]),
            tipo=TokenType(payload["type"]),
            jti=payload["jti"],
            expires_at=datetime.fromtimestamp(payload["exp"], tz=UTC),
        )
    except (KeyError, ValueError) as exc:
        raise TokenInvalidError("Payload do token malformado.") from exc


def gerar_token_opaco() -> str:
    """Token aleatorio para fluxos que nao usam JWT (ex: recuperacao de
    senha), enviado ao usuario e nunca armazenado em texto puro."""
    return secrets.token_urlsafe(32)


def hash_token_opaco(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()
