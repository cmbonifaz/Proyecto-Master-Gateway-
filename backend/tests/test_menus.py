# -*- coding: utf-8 -*-
"""
test_menus.py — Pruebas para la obtención del árbol de menús recursivos usando CTE.
"""
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User
from app.models.role import Role
from app.models.menu import Menu
from app.models.role_menu import RoleMenu
from app.core.security import hash_password, create_token

pytestmark = pytest.mark.asyncio


async def _get_auth_headers(user_id: str, role_id: str) -> dict:
    token = create_token(user_id, "access_token", {"role_id": role_id})
    return {"Authorization": f"Bearer {token}"}


async def test_recursive_menu_tree(client: AsyncClient, db: AsyncSession):
    # 1. Crear estructura
    user = User(
        email="user_menu@example.com",
        password_hash=hash_password("UserPass123!"),
        estado="ACTIVO"
    )
    role = Role(
        nombre="COMPRADOR",
        estado="ACTIVO"
    )
    db.add_all([user, role])
    await db.flush()

    # Menú Padre (Contenedor)
    menu_parent = Menu(
        texto="Gestión de Compras",
        orden="001",
        estado="ACTIVO"
    )
    db.add(menu_parent)
    await db.flush()

    # Menú Hijo
    menu_child = Menu(
        texto="Ver Catálogo",
        url="/compras/catalogo",
        orden="001",
        parent_id=menu_parent.id,
        estado="ACTIVO"
    )
    db.add(menu_child)
    await db.flush()

    # Asociar rol al menú hijo únicamente
    # El CTE debe arrastrar al menú padre para evitar orfandad
    role_menu = RoleMenu(
        role_id=role.id,
        menu_id=menu_child.id
    )
    db.add(role_menu)
    await db.commit()

    headers = await _get_auth_headers(user.id, role.id)
    response = await client.get("/api/menus/tree", headers=headers)
    assert response.status_code == 200
    
    tree = response.json()
    assert len(tree) == 1
    # Valida jerarquía recursiva
    assert tree[0]["texto"] == "Gestión de Compras"
    assert len(tree[0]["children"]) == 1
    assert tree[0]["children"][0]["texto"] == "Ver Catálogo"
    assert tree[0]["children"][0]["url"] == "/compras/catalogo"
