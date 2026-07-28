# -*- coding: utf-8 -*-
"""
test_roles.py — Pruebas para la creacion, validacion y gestion de Roles.
Cubre CRUD completo, proteccion del rol ADMIN, permisos y asignaciones con 404.
"""
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User
from app.models.role import Role
from app.models.module import Module
from app.models.menu import Menu
from app.models.user_role import UserRole
from app.core.security import hash_password, create_token

pytestmark = pytest.mark.asyncio


async def _get_auth_headers(user_id: str, role_id: str = "admin-role") -> dict:
    token = create_token(user_id, "access_token", {"role_id": role_id})
    return {"Authorization": f"Bearer {token}"}


async def _make_admin(db: AsyncSession, email: str = "admin_roles@example.com") -> User:
    admin = User(email=email, password_hash=hash_password("AdminPass123!"), estado="ACTIVO")
    db.add(admin)
    await db.commit()
    return admin


# ── POST / — Crear rol ────────────────────────────────────────────────────────

async def test_create_role_regex_validation(client: AsyncClient, db: AsyncSession):
    admin = await _make_admin(db)
    headers = await _get_auth_headers(admin.id)

    # Nombre con minusculas — invalido
    response = await client.post("/api/roles/", json={"nombre": "vendedor", "descripcion": "Rol"}, headers=headers)
    assert response.status_code == 422

    # Nombre valido en mayusculas
    response = await client.post("/api/roles/", json={"nombre": "VENDEDOR_PRINCIPAL", "descripcion": "Rol"}, headers=headers)
    assert response.status_code == 201
    assert response.json()["nombre"] == "VENDEDOR_PRINCIPAL"


async def test_create_role_duplicate_name(client: AsyncClient, db: AsyncSession):
    """Crear rol con nombre duplicado retorna 400."""
    admin = await _make_admin(db, email="admin_duprol@example.com")
    headers = await _get_auth_headers(admin.id)

    await client.post("/api/roles/", json={"nombre": "ROL_UNICO", "descripcion": "X"}, headers=headers)
    response = await client.post("/api/roles/", json={"nombre": "ROL_UNICO", "descripcion": "Y"}, headers=headers)
    assert response.status_code == 400
    assert "ya existe" in response.json()["detail"].lower()


# ── GET / — Listar roles ──────────────────────────────────────────────────────

async def test_list_roles(client: AsyncClient, db: AsyncSession):
    """GET / retorna lista de roles activos."""
    admin = await _make_admin(db, email="admin_listrol@example.com")
    headers = await _get_auth_headers(admin.id)

    await client.post("/api/roles/", json={"nombre": "ROL_LISTA_A", "descripcion": "A"}, headers=headers)
    await client.post("/api/roles/", json={"nombre": "ROL_LISTA_B", "descripcion": "B"}, headers=headers)

    response = await client.get("/api/roles/", headers=headers)
    assert response.status_code == 200
    names = [r["nombre"] for r in response.json()]
    assert "ROL_LISTA_A" in names
    assert "ROL_LISTA_B" in names


# ── GET /{id} — Obtener rol ───────────────────────────────────────────────────

async def test_get_role_by_id(client: AsyncClient, db: AsyncSession):
    """GET /{id} retorna el rol correctamente."""
    admin = await _make_admin(db, email="admin_getrol@example.com")
    headers = await _get_auth_headers(admin.id)

    create_resp = await client.post("/api/roles/", json={"nombre": "ROL_GET", "descripcion": "X"}, headers=headers)
    role_id = create_resp.json()["id"]

    response = await client.get(f"/api/roles/{role_id}", headers=headers)
    assert response.status_code == 200
    assert response.json()["nombre"] == "ROL_GET"


async def test_get_role_not_found(client: AsyncClient, db: AsyncSession):
    """GET /{id} con ID inexistente retorna 404."""
    admin = await _make_admin(db, email="admin_getnfrol@example.com")
    headers = await _get_auth_headers(admin.id)

    response = await client.get("/api/roles/00000000-0000-0000-0000-000000000000", headers=headers)
    assert response.status_code == 404


# ── GET /{id}/permissions ─────────────────────────────────────────────────────

async def test_get_role_permissions(client: AsyncClient, db: AsyncSession):
    """GET /{id}/permissions retorna usuarios, modulos y menus asignados."""
    admin = await _make_admin(db, email="admin_perms@example.com")
    headers = await _get_auth_headers(admin.id)

    create_resp = await client.post("/api/roles/", json={"nombre": "ROL_PERMS", "descripcion": "X"}, headers=headers)
    role_id = create_resp.json()["id"]

    response = await client.get(f"/api/roles/{role_id}/permissions", headers=headers)
    assert response.status_code == 200
    body = response.json()
    assert "users" in body
    assert "modules" in body
    assert "menus" in body
    assert isinstance(body["users"], list)


async def test_get_role_permissions_not_found(client: AsyncClient, db: AsyncSession):
    """GET /{id}/permissions con ID inexistente retorna 404."""
    admin = await _make_admin(db, email="admin_permsnf@example.com")
    headers = await _get_auth_headers(admin.id)

    response = await client.get(
        "/api/roles/00000000-0000-0000-0000-000000000000/permissions", headers=headers
    )
    assert response.status_code == 404


# ── PUT /{id} — Actualizar rol ────────────────────────────────────────────────

async def test_update_role(client: AsyncClient, db: AsyncSession):
    """PUT /{id} actualiza la descripcion de un rol."""
    admin = await _make_admin(db, email="admin_updrol@example.com")
    headers = await _get_auth_headers(admin.id)

    create_resp = await client.post("/api/roles/", json={"nombre": "ROL_UPDATE", "descripcion": "Original"}, headers=headers)
    role_id = create_resp.json()["id"]

    update_resp = await client.put(
        f"/api/roles/{role_id}",
        json={"descripcion": "Actualizado"},
        headers=headers
    )
    assert update_resp.status_code == 200
    assert update_resp.json()["descripcion"] == "Actualizado"


async def test_update_role_not_found(client: AsyncClient, db: AsyncSession):
    """PUT /{id} con ID inexistente retorna 404."""
    admin = await _make_admin(db, email="admin_updnfrol@example.com")
    headers = await _get_auth_headers(admin.id)

    response = await client.put(
        "/api/roles/00000000-0000-0000-0000-000000000000",
        json={"descripcion": "X"},
        headers=headers
    )
    assert response.status_code == 404


# ── DELETE /{id} — Eliminar rol ───────────────────────────────────────────────

async def test_delete_admin_role_protected(client: AsyncClient, db: AsyncSession):
    """DELETE del rol ADMIN esta protegido y retorna 400."""
    admin = await _make_admin(db, email="admin_deladmin@example.com")
    headers = await _get_auth_headers(admin.id)

    # Crear el rol ADMIN
    create_resp = await client.post("/api/roles/", json={"nombre": "ADMIN", "descripcion": "Admin"}, headers=headers)
    role_id = create_resp.json()["id"]

    response = await client.delete(f"/api/roles/{role_id}", headers=headers)
    assert response.status_code == 400
    assert "ADMINISTRADOR" in response.json()["detail"]


async def test_role_assignments(client: AsyncClient, db: AsyncSession):
    admin = User(
        email="admin_role_assignments@example.com",
        password_hash=hash_password("AdminPass123!"),
        estado="ACTIVO"
    )
    user_test = User(email="test_assign@example.com", password_hash=hash_password("UserPass123!"), estado="ACTIVO")
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

    # Delete role without active users (should succeed)
    res_del_role = await client.delete(f"/api/roles/{role.id}", headers=headers)
    assert res_del_role.status_code == 200


# ── Asignaciones con 404 ──────────────────────────────────────────────────────

async def test_assign_user_to_role_role_not_found(client: AsyncClient, db: AsyncSession):
    """Asignar usuario a rol inexistente retorna 404."""
    admin = await _make_admin(db, email="admin_rnfassign@example.com")
    user = User(email="user_rnf@example.com", password_hash=hash_password("Pass123!"), estado="ACTIVO")
    db.add(user)
    await db.commit()
    headers = await _get_auth_headers(admin.id)

    response = await client.post(
        f"/api/roles/00000000-0000-0000-0000-000000000000/users?user_id={user.id}",
        headers=headers
    )
    assert response.status_code == 404


async def test_assign_module_to_role_module_not_found(client: AsyncClient, db: AsyncSession):
    """Asignar modulo inexistente a un rol retorna 404."""
    admin = await _make_admin(db, email="admin_mnfassign@example.com")
    headers = await _get_auth_headers(admin.id)

    create_resp = await client.post("/api/roles/", json={"nombre": "ROL_MODNF", "descripcion": "X"}, headers=headers)
    role_id = create_resp.json()["id"]

    response = await client.post(
        f"/api/roles/{role_id}/modules?module_id=00000000-0000-0000-0000-000000000000",
        headers=headers
    )
    assert response.status_code == 404


async def test_assign_menu_to_role_menu_not_found(client: AsyncClient, db: AsyncSession):
    """Asignar menu inexistente a un rol retorna 404."""
    admin = await _make_admin(db, email="admin_menunfassign@example.com")
    headers = await _get_auth_headers(admin.id)

    create_resp = await client.post("/api/roles/", json={"nombre": "ROL_MENUNF", "descripcion": "X"}, headers=headers)
    role_id = create_resp.json()["id"]

    response = await client.post(
        f"/api/roles/{role_id}/menus?menu_id=00000000-0000-0000-0000-000000000000",
        headers=headers
    )
    assert response.status_code == 404
