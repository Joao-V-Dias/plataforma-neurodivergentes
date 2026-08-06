"""Fixtures compartilhadas dos testes.

Isolamento de banco: cada teste roda dentro de uma transacao propria que e
sempre revertida ao final (padrao "join a transacao externa" do
SQLAlchemy 2.0 para suites de teste). Isso permite escrever no banco real
em cada teste sem precisar limpar tabelas manualmente ou usar um banco
separado."""

from collections.abc import AsyncGenerator

import pytest_asyncio
import redis.asyncio as redis_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.database import engine, get_db
from app.core.security import hash_password
from app.main import app
from app.models.usuario import Papel, Usuario
from app.repositories import usuario_repository


@pytest_asyncio.fixture(autouse=True)
async def limpar_rate_limit_redis() -> AsyncGenerator[None, None]:
    """O rate limiting (Parte 2) usa Redis compartilhado por IP; sem isso,
    testes que fazem varios logins na mesma janela de 1 minuto derrubariam
    uns aos outros com 429. So a suite de rate limiting deve saturar o
    limite de proposito - por isso zeramos antes de cada teste."""
    settings = get_settings()
    r = redis_asyncio.from_url(settings.redis_url)
    try:
        await r.flushdb()
    except Exception:
        pass
    finally:
        await r.aclose()
    yield


@pytest_asyncio.fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    async with engine.connect() as connection:
        await connection.begin()
        session = AsyncSession(
            bind=connection, expire_on_commit=False, join_transaction_mode="create_savepoint"
        )
        try:
            yield session
        finally:
            await session.close()
            await connection.rollback()


@pytest_asyncio.fixture
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    async def _override_get_db() -> AsyncGenerator[AsyncSession, None]:
        yield db_session

    app.dependency_overrides[get_db] = _override_get_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()


async def criar_usuario(
    db: AsyncSession,
    *,
    email: str,
    senha: str = "SenhaValida123",
    papel: Papel = Papel.ALUNO,
    is_active: bool = True,
    nome: str = "Usuario de Teste",
) -> Usuario:
    return await usuario_repository.create(
        db,
        nome=nome,
        email=email,
        senha_hash=hash_password(senha),
        papel=papel,
        is_active=is_active,
    )
