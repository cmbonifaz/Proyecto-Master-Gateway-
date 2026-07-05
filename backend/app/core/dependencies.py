# -*- coding: utf-8 -*-
"""
dependencies.py — Dependencias globales de FastAPI (Depends).
Provee: get_db, get_current_user, get_current_active_user.

Zero Trust: cada endpoint protegido verifica el JWT en cada request.
No existe sesión en memoria del lado del servidor (Stateless).
"""
from typing import Annotated
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from jose import JWTError

from app.core.database import get_db
from app.core.security import decode_token

# ── Esquema de seguridad HTTP Bearer ──────────────────────────────────────────
# Extrae el token del header: Authorization: Bearer <token>
bearer_scheme = HTTPBearer(auto_error=True)


# ── Tipos anotados reutilizables ───────────────────────────────────────────────
DBSession = Annotated[AsyncSession, Depends(get_db)]


async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(bearer_scheme)],
    db: DBSession,
) -> dict:
    """
    Dependency que extrae y valida el JWT del header Authorization.
    Retorna el payload del token si es válido.

    Zero Trust: se ejecuta en CADA request a endpoints protegidos.
    No guarda estado de sesión en el servidor.

    Raises:
        HTTP 401: Si el token es inválido, expirado o ausente.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No autenticado o token inválido",   # Mensaje genérico (no revela detalles)
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = decode_token(credentials.credentials)

        # Verificar que sea un access_token (no un temp_token o refresh_token)
        if payload.get("type") != "access_token":
            raise credentials_exception

        user_id: str = payload.get("sub")
        role_id: str = payload.get("role_id")

        if not user_id or not role_id:
            raise credentials_exception

    except JWTError:
        raise credentials_exception

    # Importación lazy para evitar circular imports
    from app.models.user import User
    from sqlalchemy import select

    result = await db.execute(
        select(User).where(User.id == user_id, User.estado == "ACTIVO")
    )
    user = result.scalar_one_or_none()

    if user is None:
        raise credentials_exception

    # Retornamos el usuario con el role_id del token (Least Privilege)
    return {"user": user, "role_id": role_id}


# ── Tipo anotado para endpoints protegidos ─────────────────────────────────────
CurrentUser = Annotated[dict, Depends(get_current_user)]
