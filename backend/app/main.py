# -*- coding: utf-8 -*-
"""
main.py — Entry point del Microservicio Maestro de Auth/Autorización.
Proyecto Parcial III — Desarrollo Seguro 2026-50.
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.core.config import settings
from app.api.router import api_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Ciclo de vida de la aplicación.
    Aquí se pueden inicializar recursos (conexión BD, caché, etc.)
    y limpiarlos al apagar.
    """
    # Startup
    print(f"🚀 {settings.APP_NAME} v{settings.APP_VERSION} iniciando...")
    yield
    # Shutdown
    print("🛑 Microservicio apagado correctamente.")


app = FastAPI(
    title=settings.APP_NAME,
    description=(
        "Microservicio Maestro de Autenticación y Autorización. "
        "Gestiona Usuarios, Roles, Módulos y Menús recursivos. "
        "Implementa Zero Trust Architecture y Shift-Left Security."
    ),
    version=settings.APP_VERSION,
    lifespan=lifespan,
    # Deshabilitar docs en producción si DEBUG=False
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
)

# ── Routers ────────────────────────────────────────────────────────────────────
app.include_router(api_router)
