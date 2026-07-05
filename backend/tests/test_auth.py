# -*- coding: utf-8 -*-
"""
test_auth.py — Pruebas para los endpoints de autenticación y flujos de login.
"""
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User
from app.models.role import Role
from app.models.user_role import UserRole
from app.core.security import hash_password

pytestmark = pytest.mark.asyncio


async def test_login_flow(client: AsyncClient, db: AsyncSession):
    # 1. Crear un usuario y un rol de prueba
    user = User(
        email="test_auth@example.com",
        password_hash=hash_password("PasswordSegura123!"),
        nombre="Test Auth User",
        estado="ACTIVO"
    )
    role = Role(
        nombre="TEST_ROLE",
        descripcion="Rol de prueba",
        estado="ACTIVO"
    )
    db.add_all([user, role])
    await db.flush()

    # Asociar rol a usuario
    user_role = UserRole(
        user_id=user.id,
        role_id=role.id,
        estado="ACTIVO"
    )
    db.add(user_role)
    await db.commit()

    # ── Paso 1: Login
    login_data = {
        "email": "test_auth@example.com",
        "password": "PasswordSegura123!"
    }
    response = await client.post("/api/auth/login", json=login_data)
    assert response.status_code == 200
    res_json = response.json()
    assert "temp_token" in res_json
    assert len(res_json["roles"]) == 1
    assert res_json["roles"][0]["nombre"] == "TEST_ROLE"

    temp_token = res_json["temp_token"]

    # ── Paso 2: Selección de rol
    select_data = {
        "temp_token": temp_token,
        "role_id": role.id
    }
    response = await client.post("/api/auth/select-role", json=select_data)
    assert response.status_code == 200
    tokens = response.json()
    assert "access_token" in tokens
    assert "refresh_token" in tokens
    assert tokens["token_type"] == "bearer"


async def test_login_invalid_credentials_returns_generic_error(client: AsyncClient):
    login_data = {
        "email": "non_existing@example.com",
        "password": "WrongPassword123!"
    }
    response = await client.post("/api/auth/login", json=login_data)
    assert response.status_code == 401
    assert response.json()["detail"] == "Correo o contraseña incorrectos"
