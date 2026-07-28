# -*- coding: utf-8 -*-
"""
test_modules.py — Pruebas para el CRUD completo de Modulos del sistema.
"""
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User
from app.core.security import hash_password, create_token

pytestmark = pytest.mark.asyncio


async def _auth_headers(user_id: str) -> dict:
    token = create_token(user_id, "access_token", {"role_id": "any-role"})
    return {"Authorization": f"Bearer {token}"}


async def _make_admin(db: AsyncSession, email: str = "admin_mod@example.com") -> User:
    admin = User(
        email=email,
        password_hash=hash_password("AdminPass123!"),
        nombre="Admin Modules",
        estado="ACTIVO"
    )
    db.add(admin)
    await db.commit()
    return admin


# ── POST / ────────────────────────────────────────────────────────────────────

async def test_create_module(client: AsyncClient, db: AsyncSession):
    """Creacion exitosa de un modulo."""
    admin = await _make_admin(db)
    headers = await _auth_headers(admin.id)

    data = {"nombre": "Modulo de Ventas", "descripcion": "Gestion de ventas"}
    response = await client.post("/api/modules/", json=data, headers=headers)
    assert response.status_code == 201
    body = response.json()
    assert body["nombre"] == "Modulo de Ventas"
    assert body["descripcion"] == "Gestion de ventas"
    assert "id" in body


# ── GET / ─────────────────────────────────────────────────────────────────────

async def test_list_modules(client: AsyncClient, db: AsyncSession):
    """Listado de modulos activos."""
    admin = await _make_admin(db, email="admin_list_mod@example.com")
    headers = await _auth_headers(admin.id)

    # Crear dos modulos
    await client.post("/api/modules/", json={"nombre": "Mod A", "descripcion": "A"}, headers=headers)
    await client.post("/api/modules/", json={"nombre": "Mod B", "descripcion": "B"}, headers=headers)

    response = await client.get("/api/modules/", headers=headers)
    assert response.status_code == 200
    names = [m["nombre"] for m in response.json()]
    assert "Mod A" in names
    assert "Mod B" in names


# ── GET /{id} ─────────────────────────────────────────────────────────────────

async def test_get_module_by_id(client: AsyncClient, db: AsyncSession):
    """Obtener un modulo por su ID."""
    admin = await _make_admin(db, email="admin_getmod@example.com")
    headers = await _auth_headers(admin.id)

    create_resp = await client.post(
        "/api/modules/", json={"nombre": "Mod Get", "descripcion": "Para GET"}, headers=headers
    )
    module_id = create_resp.json()["id"]

    response = await client.get(f"/api/modules/{module_id}", headers=headers)
    assert response.status_code == 200
    assert response.json()["nombre"] == "Mod Get"


async def test_get_module_not_found(client: AsyncClient, db: AsyncSession):
    """Obtener modulo con ID inexistente retorna 404."""
    admin = await _make_admin(db, email="admin_notfound_mod@example.com")
    headers = await _auth_headers(admin.id)

    response = await client.get("/api/modules/00000000-0000-0000-0000-000000000000", headers=headers)
    assert response.status_code == 404


# ── PUT /{id} ─────────────────────────────────────────────────────────────────

async def test_update_module(client: AsyncClient, db: AsyncSession):
    """Actualizar un modulo existente."""
    admin = await _make_admin(db, email="admin_updmod@example.com")
    headers = await _auth_headers(admin.id)

    create_resp = await client.post(
        "/api/modules/", json={"nombre": "Mod Original", "descripcion": "Original"}, headers=headers
    )
    module_id = create_resp.json()["id"]

    update_resp = await client.put(
        f"/api/modules/{module_id}",
        json={"nombre": "Mod Actualizado", "descripcion": "Actualizado"},
        headers=headers
    )
    assert update_resp.status_code == 200
    assert update_resp.json()["nombre"] == "Mod Actualizado"


async def test_update_module_not_found(client: AsyncClient, db: AsyncSession):
    """Actualizar modulo con ID inexistente retorna 404."""
    admin = await _make_admin(db, email="admin_updmod404@example.com")
    headers = await _auth_headers(admin.id)

    response = await client.put(
        "/api/modules/00000000-0000-0000-0000-000000000000",
        json={"nombre": "X", "descripcion": "X"},
        headers=headers
    )
    assert response.status_code == 404


# ── DELETE /{id} ──────────────────────────────────────────────────────────────

async def test_delete_module(client: AsyncClient, db: AsyncSession):
    """Soft delete de un modulo (cambia estado a INACTIVO)."""
    admin = await _make_admin(db, email="admin_delmod@example.com")
    headers = await _auth_headers(admin.id)

    create_resp = await client.post(
        "/api/modules/", json={"nombre": "Mod Delete", "descripcion": "Para borrar"}, headers=headers
    )
    module_id = create_resp.json()["id"]

    delete_resp = await client.delete(f"/api/modules/{module_id}", headers=headers)
    assert delete_resp.status_code == 200


async def test_delete_module_not_found(client: AsyncClient, db: AsyncSession):
    """Eliminar modulo con ID inexistente retorna 404."""
    admin = await _make_admin(db, email="admin_delmod404@example.com")
    headers = await _auth_headers(admin.id)

    response = await client.delete(
        "/api/modules/00000000-0000-0000-0000-000000000000", headers=headers
    )
    assert response.status_code == 404
