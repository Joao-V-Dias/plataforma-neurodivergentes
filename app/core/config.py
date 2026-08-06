"""Configuracao central da aplicacao, carregada a partir de variaveis de
ambiente / arquivo .env via pydantic-settings. Nenhum segredo deve ser
hardcoded neste arquivo: tudo vem do ambiente, com .env.example documentando
as chaves esperadas."""

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # --- Aplicacao ---
    app_name: str = "Plataforma de Educacao Adaptativa"
    app_env: str = "development"
    app_debug: bool = True
    api_v1_prefix: str = "/api/v1"
    secret_key: str = Field(..., description="Chave usada para assinaturas criptograficas")

    # --- CORS ---
    cors_origins: str = "http://localhost:3000"

    # --- Banco de dados ---
    database_url: str = Field(
        ..., description="URL assincrona do PostgreSQL (postgresql+asyncpg://...)"
    )

    # --- Redis ---
    redis_url: str = "redis://localhost:6379/0"

    # --- Logging ---
    log_level: str = "INFO"
    log_json: bool = True

    # --- Autenticacao / JWT ---
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 15
    refresh_token_expire_days: int = 7
    password_reset_token_expire_minutes: int = 30

    # --- Rate limiting (protecao contra brute-force) ---
    rate_limit_login: str = "5/minute"
    rate_limit_forgot_password: str = "3/minute"

    # --- LGPD ---
    lgpd_politica_versao: str = "1.0"

    # --- Sandbox de execucao de codigo (Parte 5) ---
    sandbox_docker_image: str = "python:3.12-slim"
    sandbox_timeout_segundos: int = 5
    sandbox_memoria_mb: int = 128
    sandbox_cpus: str = "0.5"
    sandbox_pids_limit: int = 64
    sandbox_max_casos_por_submissao: int = 20

    # --- Motor de IA adaptativa / Groq (Parte 6) ---
    # Isolado em app/ai - nunca exposto direto ao frontend (ver app/ai/__init__.py).
    groq_api_key: str = Field(
        default="", description="Chave da API Groq; vazia desabilita o motor de IA"
    )
    groq_modelo: str = "llama-3.3-70b-versatile"
    groq_timeout_segundos: float = 20.0
    groq_max_tokens_resposta: int = 700
    dica_niveis_maximo: int = 4

    # --- Observabilidade (Parte 8) ---
    # Metricas Prometheus (GET /metrics) - sem custo/risco externo, ligado
    # por padrao. Sentry so ativa com um DSN real (vazio = desabilitado,
    # mesmo padrao do Groq acima: nunca falha a inicializacao da app por
    # falta de uma integracao de terceiros opcional).
    metrics_enabled: bool = True
    sentry_dsn: str = Field(
        default="", description="DSN do Sentry; vazio desabilita o rastreamento de erros"
    )
    sentry_traces_sample_rate: float = 0.0

    @property
    def cors_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    @property
    def is_production(self) -> bool:
        return self.app_env.lower() == "production"


@lru_cache
def get_settings() -> Settings:
    """Settings sao cacheadas (singleton) para evitar reler o .env a cada
    chamada; em testes, sobrescreva via variaveis de ambiente antes do
    primeiro uso ou limpe o cache com get_settings.cache_clear()."""
    return Settings()
