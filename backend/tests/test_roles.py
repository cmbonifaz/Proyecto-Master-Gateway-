# -*- coding: utf-8 -*-
"""
test_roles.py — Pruebas para la creación y validación de Roles.
"""
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User
from app.models.role import Role
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


async def test_role_assignments(client: AsyncClient, db: AsyncSession):
    from app.models.module import Module
    from app.models.menu import Menu
    
    admin = User(
        email="admin_role_assignments@example.com",
        password_hash=hash_password("AdminPass123!"),
        estado="ACTIVO"
    )
    user_test = User(
        email="test_assign@example.com",
        password_hash=hash_password("UserPass123!"),
        estado="ACTIVO"
    )
    role = Role(nombre="TEST_ROLE_ASSIGN", estado="ACTIVO")
    module = Module(nombre="Test Module", descripcion="Modulo de prueba")
    menu = Menu(texto="Test Menu", url="/test/menu")
    
    db.add_all([admin, user_test, role, module, menu])
    await db.commit()
    
    headers = await _get_auth_headers(admin.id)
    
    # Assign User to Role
    res = await client.post(f"/api/roles/{role.id}/users?user_id={user_test.id}", headers=headers)
    assert res.status_code == 200
    
    # Try deleting role with active user (should fail)
    res_del_role = await client.delete(f"/api/roles/{role.id}", headers=headers)
    assert res_del_role.status_code == 400
    assert "usuarios activos asignados" in res_del_role.json()["detail"]
    
    # Remove User from Role
    res = await client.delete(f"/api/roles/{role.id}/users/{user_test.id}", headers=headers)
    assert res.status_code == 200
    
    # Assign Module to Role
    res = await client.post(f"/api/roles/{role.id}/modules?module_id={module.id}", headers=headers)
    assert res.status_code == 200
    
    # Remove Module from Role
    res = await client.delete(f"/api/roles/{role.id}/modules/{module.id}", headers=headers)
    assert res.status_code == 200
    
    # Assign Menu to Role
    res = await client.post(f"/api/roles/{role.id}/menus?menu_id={menu.id}", headers=headers)
    assert res.status_code == 200
    
    # Remove Menu from Role
    res = await client.delete(f"/api/roles/{role.id}/menus/{menu.id}", headers=headers)
    assert res.status_code == 200

    # Try deleting role without active users (should succeed)
    res_del_role = await client.delete(f"/api/roles/{role.id}", headers=headers)
    assert res_del_role.status_code == 200
