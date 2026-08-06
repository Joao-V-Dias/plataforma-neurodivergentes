"""Observabilidade (Parte 8): metricas Prometheus (latencia, contagem e
status code por rota, exportadas em GET /metrics) e rastreamento de erros
via Sentry. Ambos sao aditivos e nunca impedem a aplicacao de subir: sem
`SENTRY_DSN`, o Sentry simplesmente nao e inicializado (mesmo padrao do
motor de IA - ver app/core/config.py:groq_api_key)."""

from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator

from app.core.config import get_settings
from app.core.logging import get_logger

logger = get_logger(__name__)


def configurar_metricas(app: FastAPI) -> None:
    settings = get_settings()
    if not settings.metrics_enabled:
        return

    Instrumentator().instrument(app).expose(app, endpoint="/metrics", include_in_schema=False)
    logger.info("metricas_prometheus_habilitadas", endpoint="/metrics")


def configurar_sentry() -> None:
    settings = get_settings()
    if not settings.sentry_dsn:
        logger.info("sentry_desabilitado", motivo="SENTRY_DSN nao configurada")
        return

    import sentry_sdk

    sentry_sdk.init(
        dsn=settings.sentry_dsn,
        environment=settings.app_env,
        traces_sample_rate=settings.sentry_traces_sample_rate,
        # Nunca envie corpo de request/response por padrao - podem conter
        # dado sensivel de saude (perfil de neurodivergencia, Big Five) ou
        # senha/token; ver docs/lgpd.md.
        send_default_pii=False,
    )
    logger.info("sentry_habilitado", environment=settings.app_env)
