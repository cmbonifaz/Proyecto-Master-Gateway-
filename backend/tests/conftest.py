# -*- coding: utf-8 -*-
"""
conftest.py — Configuración de pytest y fixtures de base de datos.
Usa SQLite en memoria en CI (DATABASE_URL=sqlite+aiosqlite:///:memory:)
y PostgreSQL/Supabase en desarrollo. Cada test corre aislado con rollback.
"""
import pytest
import pytest_asyncio
from typing import AsyncGenerator
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import StaticPool
from app.core.config import settings
from app.core.database import Base, get_db
from app.main import app

# ── Engine compatible con SQLite (CI) o PostgreSQL (producción) ────────────────
_IS_SQLITE = settings.DATABASE_URL.startswith("sqlite")

if _IS_SQLITE:
    engine = create_async_engine(
        settings.DATABASE_URL,
        echo=False,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
else:
    engine = create_async_engine(settings.DATABASE_URL, echo=False)

TestingSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


@pytest_asyncio.fixture(autouse=True)
async def setup_db():
    """Crea las tablas antes de cada test y las elimina al terminar."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def db(setup_db) -> AsyncGenerator[AsyncSession, None]:
    """
    Fixture que provee una sesión de BD envuelta en una transacción.
    Todo cambio ejecutado durante el test es revertido (rollback) al terminar.
    """
    async with engine.connect() as connection:
        transaction = await connection.begin()
        async with TestingSessionLocal(bind=connection) as session:
            yield session
            await session.rollback()
        await transaction.rollback()


@pytest_asyncio.fixture
async def client(db: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """
    Fixture que provee un cliente HTTP asíncrono.
    Inyecta la sesión de pruebas con rollback en FastAPI.
    """
    async def override_get_db():
        yield db

    app.dependency_overrides[get_db] = override_get_db
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as ac:
        yield ac
    app.dependency_overrides.clear()
