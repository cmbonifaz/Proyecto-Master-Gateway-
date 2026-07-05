# -*- coding: utf-8 -*-
"""
conftest.py — Configuración de pytest y fixtures de base de datos.
Utiliza SQLite en memoria cuando DATABASE_URL es sqlite (entorno CI),
o la BD real cuando es PostgreSQL. Cada test corre en una transacción
que se revierte automáticamente (rollback) al terminar.
"""
import pytest
import asyncio
from typing import AsyncGenerator
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import StaticPool
from app.core.config import settings
from app.core.database import Base, get_db
from app.main import app

# ── Crear engine compatible con SQLite (CI) o PostgreSQL (producción) ──────────
_IS_SQLITE = settings.DATABASE_URL.startswith("sqlite")

if _IS_SQLITE:
    # SQLite en memoria para CI: StaticPool mantiene la misma conexión
    # en memoria durante toda la sesión de tests (necesario para que
    # create_all y los tests compartan la misma BD en memoria)
    engine = create_async_engine(
        settings.DATABASE_URL,
        echo=False,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
else:
    # PostgreSQL real (entorno de desarrollo/staging)
    engine = create_async_engine(settings.DATABASE_URL, echo=False)

TestingSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False
)


@pytest.fixture(scope="session")
def event_loop():
    """Crear una instancia única del loop de eventos por sesión de pruebas."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session", autouse=True)
async def setup_db():
    """
    Garantiza que las tablas existan antes de correr los tests.
    """
    async with engine.begin() as conn:
        # Crea las tablas si no existen
        await conn.run_sync(Base.metadata.create_all)
    yield
    # No eliminamos tablas al finalizar para evitar destruir Supabase accidentalmente,
    # ya que cada test corre dentro de una transacción aislada con rollback.


@pytest.fixture
async def db() -> AsyncGenerator[AsyncSession, None]:
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


@pytest.fixture
async def client(db: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """
    Fixture que provee un cliente HTTP asíncrono para consumir endpoints.
    Inyecta la sesión de pruebas con rollback automático en FastAPI.
    """
    async def override_get_db():
        yield db

    app.dependency_overrides[get_db] = override_get_db
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()
