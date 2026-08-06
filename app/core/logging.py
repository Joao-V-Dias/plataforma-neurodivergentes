"""Logging estruturado em JSON com correlacao por request-id.

Usamos `structlog` para produzir logs em JSON (um objeto por linha), o que
facilita ingestao por ferramentas de observabilidade (Parte 8). O
request-id e propagado via `contextvars`, entao qualquer log emitido durante
o processamento de uma requisicao carrega automaticamente o mesmo id,
mesmo em codigo chamado varias camadas abaixo do endpoint."""

import logging
import sys
from collections.abc import MutableMapping
from contextvars import ContextVar
from typing import Any, cast

import structlog

from app.core.config import get_settings

_request_id_ctx: ContextVar[str | None] = ContextVar("request_id", default=None)


def get_request_id() -> str | None:
    return _request_id_ctx.get()


def set_request_id(request_id: str) -> None:
    _request_id_ctx.set(request_id)


def _inject_request_id(
    _logger: object, _method_name: str, event_dict: MutableMapping[str, Any]
) -> MutableMapping[str, Any]:
    request_id = get_request_id()
    if request_id is not None:
        event_dict["request_id"] = request_id
    return event_dict


def configure_logging() -> None:
    settings = get_settings()

    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=settings.log_level.upper(),
    )

    shared_processors: list[structlog.types.Processor] = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        structlog.processors.TimeStamper(fmt="iso"),
        _inject_request_id,
    ]

    renderer = (
        structlog.processors.JSONRenderer()
        if settings.log_json
        else structlog.dev.ConsoleRenderer()
    )

    structlog.configure(
        processors=[*shared_processors, structlog.stdlib.ProcessorFormatter.wrap_for_formatter],
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

    formatter = structlog.stdlib.ProcessorFormatter(
        foreign_pre_chain=shared_processors,
        processors=[structlog.stdlib.ProcessorFormatter.remove_processors_meta, renderer],
    )

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)

    root_logger = logging.getLogger()
    root_logger.handlers = [handler]
    root_logger.setLevel(settings.log_level.upper())


def get_logger(name: str) -> structlog.stdlib.BoundLogger:
    # structlog.get_logger() e deliberadamente pouco tipado a montante
    # (devolve o wrapper configurado em tempo de execucao); o cast reflete
    # o que configure_logging() de fato registra como wrapper_class acima.
    return cast(structlog.stdlib.BoundLogger, structlog.get_logger(name))
