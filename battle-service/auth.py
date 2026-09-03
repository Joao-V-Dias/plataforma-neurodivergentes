"""Validacao do access token JWT emitido pela API principal
(app/core/security.py). Usa o mesmo SECRET_KEY/JWT_ALGORITHM (config.py)
para nao duplicar segredo com valor diferente - qualquer token valido para
a API principal tambem e valido aqui, sem chamar a API principal."""

import uuid

import jwt

from config import get_settings


class TokenInvalido(Exception):
    pass


def validar_token(token: str) -> uuid.UUID:
    """Decodifica e valida o token, retornando o id do usuario autenticado.
    Aceita apenas tokens do tipo 'access' (mesmo formato de
    app/core/security.py:create_access_token)."""
    settings = get_settings()
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.jwt_algorithm])
    except jwt.InvalidTokenError as exc:
        raise TokenInvalido(str(exc)) from exc

    if payload.get("type") != "access":
        raise TokenInvalido("Token nao e do tipo access")

    try:
        return uuid.UUID(payload["sub"])
    except (KeyError, ValueError) as exc:
        raise TokenInvalido("Payload sem 'sub' valido") from exc
