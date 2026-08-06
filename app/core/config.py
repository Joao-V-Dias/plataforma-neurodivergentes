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
    database_url: str = Field(..., description="URL assincrona do PostgreSQL (postgresql+asyncpg://...)")

    # --- Redis ---
    redis_url: str = "redis://localhost:6379/0"

    # --- Logging ---
    log_level: str = "INFO"
    log_json: bool = True

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
    return Settings()  # type: ignore[call-arg]
