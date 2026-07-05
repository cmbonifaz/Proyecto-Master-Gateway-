# -*- coding: utf-8 -*-
"""
test_users.py — Pruebas para la gestión de usuarios (CRUD) y validación de seguridad Shift-Left.
"""
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User
from app.core.security import hash_password, create_token

pytestmark = pytest.mark.asyncio


async def _get_auth_headers(user_id: str, role_id: str = "some-role") -> dict:
    token = create_token(user_id, "access_token", {"role_id": role_id})
    return {"Authorization": f"Bearer {token}"}


async def test_create_user_strength_password_validation(client: AsyncClient, db: AsyncSession):
    # Crear un usuario administrador ficticio para la cabecera
    admin = User(
        email="admin@example.com",
        password_hash=hash_password("AdminPass123!"),
        estado="ACTIVO"
    )
    db.add(admin)
    await db.commit()
    headers = await _get_auth_headers(admin.id)

    # 1. Contraseña sin mayúsculas
    user_data = {
        "email": "user1@example.com",
        "nombre": "User One",
        "password": "weakpassword123!"
    }
    response = await client.post("/api/users/", json=user_data, headers=headers)
    assert response.status_code == 422  # Error de validación Pydantic

    # 2. Contraseña sin número
    user_data["password"] = "WeakPassword!"
    response = await client.post("/api/users/", json=user_data, headers=headers)
    assert response.status_code == 422

    # 3. Contraseña sin carácter especial
    user_data["password"] = "WeakPassword123"
    response = await client.post("/api/users/", json=user_data, headers=headers)
    assert response.status_code == 422

    # 4. Contraseña fuerte exitosa
    user_data["password"] = "StrongPassword123!"
    response = await client.post("/api/users/", json=user_data, headers=headers)
    assert response.status_code == 201
    assert response.json()["email"] == "user1@example.com"
