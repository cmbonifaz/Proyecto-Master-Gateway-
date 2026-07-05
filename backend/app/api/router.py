# -*- coding: utf-8 -*-
"""
router.py — Agregador central de todos los routers de la API.
Cada módulo de la aplicación tiene su propio router con prefix y tags.
"""
from fastapi import APIRouter
from app.api.endpoints import auth, internals, users, roles, modules, menus

api_router = APIRouter(prefix="/api")

# ── Auth ───────────────────────────────────────────────────────────────────────
api_router.include_router(auth.router, prefix="/auth", tags=["Autenticación"])

# ── Internals (microservicios hijos) ───────────────────────────────────────────
api_router.include_router(internals.router, prefix="/internals", tags=["Internals"])

# ── CRUD ───────────────────────────────────────────────────────────────────────
api_router.include_router(users.router,   prefix="/users",   tags=["Usuarios"])
api_router.include_router(roles.router,   prefix="/roles",   tags=["Roles"])
api_router.include_router(modules.router, prefix="/modules", tags=["Módulos"])
api_router.include_router(menus.router,   prefix="/menus",   tags=["Menús"])
