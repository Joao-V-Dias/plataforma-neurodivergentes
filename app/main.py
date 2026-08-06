"""Ponto de entrada da aplicacao FastAPI: monta middlewares, exception
handlers e routers. Mantido enxuto de proposito - a logica de negocio vive
em app/services e app/repositories, nunca aqui."""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi.middleware import SlowAPIMiddleware

from app.api.v1.auth import router as auth_router
from app.api.v1.health import router as health_router
from app.api.v1.perfis import router as perfis_router
from app.api.v1.usuarios import router as usuarios_router
from app.core.config import get_settings
from app.core.errors import register_exception_handlers
from app.core.logging import configure_logging, get_logger
from app.core.middleware import RequestIDMiddleware
from app.core.rate_limit import limiter
from app.core.security_headers import SecurityHeadersMiddleware

settings = get_settings()
configure_logging()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncGenerator[None, None]:
    logger.info("app_startup", app_env=settings.app_env)
    yield
    logger.info("app_shutdown")


app = FastAPI(
    title=settings.app_name,
    debug=settings.app_debug,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)

app.state.limiter = limiter

# Request-id primeiro para que todo log subsequente (inclusive de outros
# middlewares) ja carregue o id de correlacao.
app.add_middleware(RequestIDMiddleware)
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(SlowAPIMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

register_exception_handlers(app)

app.include_router(health_router, prefix=settings.api_v1_prefix)
app.include_router(auth_router, prefix=settings.api_v1_prefix)
app.include_router(usuarios_router, prefix=settings.api_v1_prefix)
app.include_router(perfis_router, prefix=settings.api_v1_prefix)
