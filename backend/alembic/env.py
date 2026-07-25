# -*- coding: utf-8 -*-
"""
env.py — Configuración del entorno de Alembic.
Usa SQLAlchemy SYNC (psycopg2) para las migraciones.
La app en runtime usa async (asyncpg), pero Alembic CLI es siempre sync.
"""
from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from sqlalchemy.engine import Connection
from alembic import context
import sys
import os

# Asegura que el paquete 'app' sea encontrado desde backend/
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Importar settings y todos los modelos (necesario para autogenerate)
from app.core.config import settings
from app.core.database import Base
import app.models  # noqa: F401 — carga todos los modelos para que Alembic los detecte

config = context.config

# Configurar logging desde alembic.ini
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Apuntar al metadata de nuestros modelos (para autogenerate)
target_metadata = Base.metadata


def _build_sync_url(url: str) -> str:
    """
    Convierte la DATABASE_URL de la app (asyncpg) a una URL sync (psycopg2).
    Soporta: postgresql+asyncpg://, postgresql://, postgres://
    Elimina parámetros SSL del query string (psycopg2 los ignora o falla con ellos).
    """
    sync_url = url
    # Reemplazar driver async por sync
    sync_url = sync_url.replace("postgresql+asyncpg://", "postgresql+psycopg2://")
    sync_url = sync_url.replace("postgres+asyncpg://", "postgresql+psycopg2://")
    sync_url = sync_url.replace("sqlite+aiosqlite://", "sqlite://")
    # Normalizar postgres:// a postgresql+psycopg2://
    if sync_url.startswith("postgres://"):
        sync_url = "postgresql+psycopg2://" + sync_url[len("postgres://"):]
    # Normalizar postgresql:// (sin driver) a psycopg2
    if sync_url.startswith("postgresql://"):
        sync_url = "postgresql+psycopg2://" + sync_url[len("postgresql://"):]
    # Eliminar parámetros SSL del query string que psycopg2 no entiende igual
    for param in ["?ssl=true", "&ssl=true", "?sslmode=require", "&sslmode=require",
                  "?sslmode=disable", "&sslmode=disable"]:
        sync_url = sync_url.replace(param, "")
    return sync_url


# Configurar la URL sync en el config de Alembic
config.set_main_option("sqlalchemy.url", _build_sync_url(settings.DATABASE_URL))


def run_migrations_offline() -> None:
    """Ejecuta migraciones en modo offline (genera SQL sin conexión activa)."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Ejecuta migraciones en modo online usando engine SYNC (psycopg2)."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
        )
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
