"""Configuracao do battle-service, carregada de variaveis de ambiente /
arquivo .env via pydantic-settings - mesmo padrao usado pela API principal
(app/core/config.py). Nenhum segredo hardcoded: SECRET_KEY vem do ambiente
e precisa ser IDENTICO ao da API principal (e o segredo que assina o
access token que o usuario apresenta aqui)."""

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

    secret_key: str = Field(..., description="Mesmo SECRET_KEY da API principal (app/.env)")
    jwt_algorithm: str = "HS256"


@lru_cache
def get_settings() -> Settings:
    """Settings sao cacheadas (singleton); em testes, sobrescreva via
    variaveis de ambiente antes do primeiro uso ou limpe o cache com
    get_settings.cache_clear()."""
    return Settings()
