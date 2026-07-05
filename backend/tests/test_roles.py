# -*- coding: utf-8 -*-
"""
test_roles.py — Pruebas para la creación y validación de Roles.
"""
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User
from app.core.security import hash_password, create_token

pytestmark = pytest.mark.asyncio


async def _get_auth_headers(user_id: str, role_id: str = "admin-role") -> dict:
    token = create_token(user_id, "access_token", {"role_id": role_id})
    return {"Authorization": f"Bearer {token}"}


async def test_create_role_regex_validation(client: AsyncClient, db: AsyncSession):
    admin = User(
        email="admin_role@example.com",
        password_hash=hash_password("AdminPass123!"),
        estado="ACTIVO"
    )
    db.add(admin)
    await db.commit()
    headers = await _get_auth_headers(admin.id)

    # 1. Nombre de rol inválido (minúsculas no permitidas)
    role_data = {
        "nombre": "vendedor",
        "descripcion": "Rol de ventas"
    }
    response = await client.post("/api/roles/", json=role_data, headers=headers)
    assert response.status_code == 422  # Pydantic regex error

    # 2. Nombre de rol válido (automatiza conversión a mayúsculas y valida)
    role_data["nombre"] = "VENDEDOR_PRINCIPAL"
    response = await client.post("/api/roles/", json=role_data, headers=headers)
    assert response.status_code == 201
    assert response.json()["nombre"] == "VENDEDOR_PRINCIPAL"
