# -*- coding: utf-8 -*-
"""
database.py — Configuración de SQLAlchemy async con PostgreSQL.
Provee: engine, SessionLocal (async), y la función get_db para Depends.
"""
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from app.core.config import settings


# ── Motor de Base de Datos (async) ─────────────────────────────────────────────
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,      # Muestra SQL en consola solo en modo DEBUG
    pool_pre_ping=True,       # Verifica conexión antes de usar del pool
    pool_size=10,
    max_overflow=20,
)

# ── Fábrica de sesiones ────────────────────────────────────────────────────────
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False,
)


# ── Clase Base para todos los modelos ORM ──────────────────────────────────────
class Base(DeclarativeBase):
    """
    Clase base de SQLAlchemy.
    Todos los modelos deben heredar de esta clase (o de BaseAudit que hereda de esta).
    """
    pass


# ── Dependency para inyectar la sesión en cada endpoint ────────────────────────
async def get_db() -> AsyncSession:
    """
    Genera una sesión de base de datos por request.
    Garantiza cierre automático al finalizar (context manager).
    Usar con: db: AsyncSession = Depends(get_db)
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
