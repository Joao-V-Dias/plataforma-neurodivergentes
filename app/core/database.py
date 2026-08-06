"""Conexao assincrona com o PostgreSQL via SQLAlchemy 2.0.

Expoe uma engine assincrona unica (reaproveitada por toda a aplicacao) e
uma dependency `get_db` para injetar sessoes por requisicao em endpoints
FastAPI, garantindo que cada requisicao tenha sua propria sessao e que ela
seja sempre fechada ao final."""

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import get_settings

settings = get_settings()

engine = create_async_engine(
    settings.database_url,
    echo=settings.app_debug and not settings.is_production,
    pool_pre_ping=True,
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
