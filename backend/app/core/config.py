# -*- coding: utf-8 -*-
"""
config.py — Configuración centralizada de la aplicación.
Todas las variables se cargan desde variables de entorno o archivo .env
NUNCA hardcodear credenciales aquí.
"""
from pydantic_settings import BaseSettings
from pydantic import Field
from functools import lru_cache


class Settings(BaseSettings):
    # ── Aplicación ──────────────────────────────────────────────────────────────
    APP_NAME: str = "Master Auth API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False

    # ── Base de Datos ───────────────────────────────────────────────────────────
    DATABASE_URL: str = Field(
        default="postgresql+asyncpg://user:password@localhost:5432/master_auth",
        description="URL de conexión a PostgreSQL (async)"
    )

    # ── JWT ─────────────────────────────────────────────────────────────────────
    JWT_SECRET: str = Field(
        default="CHANGE_ME_IN_PRODUCTION",
        description="Clave secreta para firmar JWT. Cambiar en producción."
    )
    JWT_ALGORITHM: str = "HS256"

    # Token temporal (entre login y selección de rol)
    TEMP_TOKEN_EXPIRE_MINUTES: int = 5

    # JWT definitivo (después de seleccionar rol)
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Refresh token
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # ── Bcrypt ──────────────────────────────────────────────────────────────────
    BCRYPT_ROUNDS: int = 12   # Cost factor — resistente a fuerza bruta

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """
    Retorna la instancia singleton de Settings.
    Usar con FastAPI Depends: Depends(get_settings)
    """
    return Settings()


settings = get_settings()
