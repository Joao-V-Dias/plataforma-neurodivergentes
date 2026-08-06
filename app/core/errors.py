"""Exception handlers centralizados. Toda excecao que chega ate aqui e
convertida no schema unico `ErrorResponse` (app/schemas/error.py), evitando
que detalhes internos (stack trace, tipo de excecao Python, etc.) vazem
para o cliente em erros nao tratados."""

from typing import Any

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from slowapi.errors import RateLimitExceeded
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.logging import get_logger, get_request_id
from app.schemas.error import ErrorDetail, ErrorResponse

logger = get_logger(__name__)


def _error_response(
    status_code: int, code: str, message: str, fields: dict[str, Any] | None = None
) -> JSONResponse:
    body = ErrorResponse(
        error=ErrorDetail(code=code, message=message, fields=fields),
        request_id=get_request_id(),
    )
    return JSONResponse(status_code=status_code, content=body.model_dump(mode="json"))


async def http_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    # Starlette so despacha esta funcao para excecoes StarletteHTTPException
    # (registro em register_exception_handlers abaixo) - a assinatura aqui
    # e Exception so porque e o que add_exception_handler exige; o assert
    # documenta e restaura o tipo especifico para o resto da funcao.
    assert isinstance(exc, StarletteHTTPException)
    return _error_response(
        status_code=exc.status_code,
        code="http_error",
        message=str(exc.detail),
    )


async def validation_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    assert isinstance(exc, RequestValidationError)
    fields: dict[str, list[str]] = {}
    for error in exc.errors():
        field_path = ".".join(str(loc) for loc in error["loc"] if loc != "body")
        fields.setdefault(field_path or "__root__", []).append(error["msg"])

    return _error_response(
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
        code="validation_error",
        message="Um ou mais campos sao invalidos.",
        fields=fields,
    )


async def rate_limit_exceeded_handler(request: Request, exc: Exception) -> JSONResponse:
    assert isinstance(exc, RateLimitExceeded)
    return _error_response(
        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        code="rate_limited",
        message="Muitas tentativas em um curto periodo. Tente novamente em instantes.",
    )


async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.exception("unhandled_exception", path=str(request.url.path), error=str(exc))
    return _error_response(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        code="internal_error",
        message="Ocorreu um erro interno inesperado.",
    )


def register_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(RateLimitExceeded, rate_limit_exceeded_handler)
    app.add_exception_handler(Exception, unhandled_exception_handler)
