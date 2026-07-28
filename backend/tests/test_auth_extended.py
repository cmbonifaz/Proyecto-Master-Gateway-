# -*- coding: utf-8 -*-
"""
test_auth_extended.py — Pruebas adicionales para los endpoints de autenticacion:
/register (exito, duplicados activo/inactivo), /select-role invalido, /refresh-token invalido.
"""
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User
from app.models.role import Role
from app.models.user_role import UserRole
from app.core.security import hash_password, create_token

pytestmark = pytest.mark.asyncio


# ── /register ────────────────────────────────────────────────────────────────

async def test_register_success(client: AsyncClient):
    """Registro exitoso de un usuario nuevo sin roles."""
    data = {
        "email": "nuevo@example.com",
        "nombre": "Nuevo Usuario",
        "password": "Password123!"
    }
    response = await client.post("/api/auth/register", json=data)
    assert response.status_code == 201
    assert "Registro exitoso" in response.json()["detail"]


async def test_register_duplicate_active_email(client: AsyncClient, db: AsyncSession):
    """Registro rechazado si el correo ya existe y esta ACTIVO."""
    user = User(
        email="duplicado@example.com",
        password_hash=hash_password("Password123!"),
        nombre="Ya Existe",
        estado="ACTIVO"
    )
    db.add(user)
    await db.commit()

    data = {
        "email": "duplicado@example.com",
        "nombre": "Intento Duplicado",
        "password": "Password123!"
    }
    response = await client.post("/api/auth/register", json=data)
    assert response.status_code == 400
    assert "ya esta registrado" in response.json()["detail"].lower() or \
           "ya está registrado" in response.json()["detail"].lower()


async def test_register_duplicate_inactive_email(client: AsyncClient, db: AsyncSession):
    """Registro rechazado con mensaje especifico si el correo existe pero esta INACTIVO."""
    user = User(
        email="inactivo@example.com",
        password_hash=hash_password("Password123!"),
        nombre="Inactivo",
        estado="INACTIVO"
    )
    db.add(user)
    await db.commit()

    data = {
        "email": "inactivo@example.com",
        "nombre": "Reintento Inactivo",
        "password": "Password123!"
    }
    response = await client.post("/api/auth/register", json=data)
    assert response.status_code == 400
    assert "INACTIVO" in response.json()["detail"]


# ── /select-role ─────────────────────────────────────────────────────────────

async def test_select_role_with_invalid_temp_token(client: AsyncClient, db: AsyncSession):
    """Seleccion de rol rechazada si el temp_token es invalido."""
    role = Role(nombre="ROLE_SELECTTEST", estado="ACTIVO")
    db.add(role)
    await db.commit()

    data = {
        "temp_token": "token.invalido.aqui",
        "role_id": role.id
    }
    response = await client.post("/api/auth/select-role", json=data)
    assert response.status_code == 401


async def test_select_role_with_wrong_token_type(client: AsyncClient, db: AsyncSession):
    """Seleccion de rol rechazada si se usa un access_token en vez de temp_token."""
    user = User(
        email="wrongtype@example.com",
        password_hash=hash_password("Password123!"),
        nombre="Wrong Type",
        estado="ACTIVO"
    )
    role = Role(nombre="ROLE_WRONGTYPE", estado="ACTIVO")
    db.add_all([user, role])
    await db.commit()

    # Crear un access_token (tipo incorrecto para select-role)
    wrong_token = create_token(user.id, "access_token", {"role_id": role.id})
    data = {"temp_token": wrong_token, "role_id": role.id}
    response = await client.post("/api/auth/select-role", json=data)
    assert response.status_code == 401


# ── /refresh-token ────────────────────────────────────────────────────────────

async def test_refresh_token_with_invalid_token(client: AsyncClient, db: AsyncSession):
    """Renovacion de token rechazada si el refresh_token es invalido."""
    role = Role(nombre="ROLE_REFRESHTEST", estado="ACTIVO")
    db.add(role)
    await db.commit()

    response = await client.post(
        f"/api/auth/refresh-token?role_id={role.id}",
        json={"refresh_token": "token.invalido.aqui"}
    )
    assert response.status_code == 401


async def test_refresh_token_with_wrong_type(client: AsyncClient, db: AsyncSession):
    """Renovacion rechazada si se usa access_token en vez de refresh_token."""
    user = User(
        email="wrongrefresh@example.com",
        password_hash=hash_password("Password123!"),
        nombre="Wrong Refresh",
        estado="ACTIVO"
    )
    role = Role(nombre="ROLE_WRONGREFRESH", estado="ACTIVO")
    db.add_all([user, role])
    await db.commit()

    # Crear un access_token (tipo incorrecto para refresh)
    wrong_token = create_token(user.id, "access_token", {"role_id": role.id})
    response = await client.post(
        f"/api/auth/refresh-token?role_id={role.id}",
        json={"refresh_token": wrong_token}
    )
    assert response.status_code == 401
