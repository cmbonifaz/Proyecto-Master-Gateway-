# -*- coding: utf-8 -*-
"""
test_users.py — Pruebas para la gestion de usuarios (CRUD completo),
validacion de seguridad Shift-Left, PATCH /activate y asignacion de roles.
"""
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User
from app.models.role import Role
from app.core.security import hash_password, create_token

pytestmark = pytest.mark.asyncio


async def _get_auth_headers(user_id: str, role_id: str = "some-role") -> dict:
    token = create_token(user_id, "access_token", {"role_id": role_id})
    return {"Authorization": f"Bearer {token}"}


# ── POST / — Creacion de usuario ─────────────────────────────────────────────

async def test_create_user_strength_password_validation(client: AsyncClient, db: AsyncSession):
    admin = User(
        email="admin@example.com",
        password_hash=hash_password("AdminPass123!"),
        estado="ACTIVO"
    )
    db.add(admin)
    await db.commit()
    headers = await _get_auth_headers(admin.id)

    # 1. Contraseña sin mayusculas
    user_data = {"email": "user1@example.com", "nombre": "User One", "password": "weakpassword123!"}
    response = await client.post("/api/users/", json=user_data, headers=headers)
    assert response.status_code == 422

    # 2. Contraseña sin numero
    user_data["password"] = "WeakPassword!"
    response = await client.post("/api/users/", json=user_data, headers=headers)
    assert response.status_code == 422

    # 3. Contraseña sin caracter especial
    user_data["password"] = "WeakPassword123"
    response = await client.post("/api/users/", json=user_data, headers=headers)
    assert response.status_code == 422

    # 4. Contraseña fuerte exitosa
    user_data["password"] = "StrongPassword123!"
    response = await client.post("/api/users/", json=user_data, headers=headers)
    assert response.status_code == 201
    assert response.json()["email"] == "user1@example.com"


async def test_create_user_duplicate_active_email(client: AsyncClient, db: AsyncSession):
    """Crear usuario con email activo duplicado retorna 400."""
    admin = User(email="admin_dup@example.com", password_hash=hash_password("Admin123!"), estado="ACTIVO")
    existing = User(email="exist@example.com", password_hash=hash_password("Pass123!"), estado="ACTIVO")
    db.add_all([admin, existing])
    await db.commit()
    headers = await _get_auth_headers(admin.id)

    data = {"email": "exist@example.com", "nombre": "Dup", "password": "Password123!"}
    response = await client.post("/api/users/", json=data, headers=headers)
    assert response.status_code == 400
    assert "ya está registrado" in response.json()["detail"] or \
           "ya esta registrado" in response.json()["detail"].lower()


async def test_create_user_duplicate_inactive_email(client: AsyncClient, db: AsyncSession):
    """Crear usuario con email INACTIVO duplicado retorna 400 con mensaje especifico."""
    admin = User(email="admin_inact@example.com", password_hash=hash_password("Admin123!"), estado="ACTIVO")
    inactive = User(email="inact@example.com", password_hash=hash_password("Pass123!"), estado="INACTIVO")
    db.add_all([admin, inactive])
    await db.commit()
    headers = await _get_auth_headers(admin.id)

    data = {"email": "inact@example.com", "nombre": "Dup Inactive", "password": "Password123!"}
    response = await client.post("/api/users/", json=data, headers=headers)
    assert response.status_code == 400
    assert "INACTIVO" in response.json()["detail"]


# ── GET / — Listado ───────────────────────────────────────────────────────────

async def test_list_users_returns_all(client: AsyncClient, db: AsyncSession):
    """GET / lista usuarios activos e inactivos."""
    admin = User(email="admin_list@example.com", password_hash=hash_password("Admin123!"), estado="ACTIVO")
    user_inactive = User(email="inact_list@example.com", password_hash=hash_password("Pass123!"), estado="INACTIVO")
    db.add_all([admin, user_inactive])
    await db.commit()
    headers = await _get_auth_headers(admin.id)

    response = await client.get("/api/users/", headers=headers)
    assert response.status_code == 200
    emails = [u["email"] for u in response.json()]
    assert "admin_list@example.com" in emails
    assert "inact_list@example.com" in emails


# ── GET /{id} ─────────────────────────────────────────────────────────────────

async def test_get_user_by_id(client: AsyncClient, db: AsyncSession):
    """GET /{id} retorna el usuario correctamente."""
    admin = User(email="admin_get@example.com", password_hash=hash_password("Admin123!"), estado="ACTIVO")
    target = User(email="target@example.com", password_hash=hash_password("Pass123!"), nombre="Target", estado="ACTIVO")
    db.add_all([admin, target])
    await db.commit()
    headers = await _get_auth_headers(admin.id)

    response = await client.get(f"/api/users/{target.id}", headers=headers)
    assert response.status_code == 200
    assert response.json()["email"] == "target@example.com"


async def test_get_user_not_found(client: AsyncClient, db: AsyncSession):
    """GET /{id} con ID inexistente retorna 404."""
    admin = User(email="admin_getnf@example.com", password_hash=hash_password("Admin123!"), estado="ACTIVO")
    db.add(admin)
    await db.commit()
    headers = await _get_auth_headers(admin.id)

    response = await client.get("/api/users/00000000-0000-0000-0000-000000000000", headers=headers)
    assert response.status_code == 404


# ── PUT /{id} — Actualizacion ─────────────────────────────────────────────────

async def test_update_user(client: AsyncClient, db: AsyncSession):
    """PUT /{id} actualiza nombre del usuario."""
    admin = User(email="admin_upd@example.com", password_hash=hash_password("Admin123!"), estado="ACTIVO")
    target = User(email="upd_target@example.com", password_hash=hash_password("Pass123!"), nombre="Original", estado="ACTIVO")
    db.add_all([admin, target])
    await db.commit()
    headers = await _get_auth_headers(admin.id)

    response = await client.put(
        f"/api/users/{target.id}",
        json={"nombre": "Actualizado"},
        headers=headers
    )
    assert response.status_code == 200
    assert response.json()["nombre"] == "Actualizado"


async def test_update_user_not_found(client: AsyncClient, db: AsyncSession):
    """PUT /{id} con ID inexistente retorna 404."""
    admin = User(email="admin_updnf@example.com", password_hash=hash_password("Admin123!"), estado="ACTIVO")
    db.add(admin)
    await db.commit()
    headers = await _get_auth_headers(admin.id)

    response = await client.put(
        "/api/users/00000000-0000-0000-0000-000000000000",
        json={"nombre": "X"},
        headers=headers
    )
    assert response.status_code == 404


# ── DELETE /{id} — Soft Delete ────────────────────────────────────────────────

async def test_delete_user(client: AsyncClient, db: AsyncSession):
    """DELETE /{id} realiza soft delete (estado=INACTIVO)."""
    admin = User(email="admin_del@example.com", password_hash=hash_password("Admin123!"), estado="ACTIVO")
    target = User(email="del_target@example.com", password_hash=hash_password("Pass123!"), estado="ACTIVO")
    db.add_all([admin, target])
    await db.commit()
    headers = await _get_auth_headers(admin.id)

    response = await client.delete(f"/api/users/{target.id}", headers=headers)
    assert response.status_code == 200
    assert response.json()["estado"] == "INACTIVO"


async def test_delete_user_self_forbidden(client: AsyncClient, db: AsyncSession):
    """DELETE sobre el propio usuario retorna 400."""
    admin = User(email="admin_self@example.com", password_hash=hash_password("Admin123!"), estado="ACTIVO")
    db.add(admin)
    await db.commit()
    headers = await _get_auth_headers(admin.id)

    response = await client.delete(f"/api/users/{admin.id}", headers=headers)
    assert response.status_code == 400
    assert "auto-eliminarte" in response.json()["detail"]


async def test_delete_user_not_found(client: AsyncClient, db: AsyncSession):
    """DELETE /{id} con ID inexistente retorna 404."""
    admin = User(email="admin_delnf@example.com", password_hash=hash_password("Admin123!"), estado="ACTIVO")
    db.add(admin)
    await db.commit()
    headers = await _get_auth_headers(admin.id)

    response = await client.delete(
        "/api/users/00000000-0000-0000-0000-000000000000", headers=headers
    )
    assert response.status_code == 404


# ── PATCH /{id}/activate ──────────────────────────────────────────────────────

async def test_activate_inactive_user(client: AsyncClient, db: AsyncSession):
    """PATCH /activate reactiva un usuario INACTIVO."""
    admin = User(email="admin_act@example.com", password_hash=hash_password("Admin123!"), estado="ACTIVO")
    inactive = User(email="reactive@example.com", password_hash=hash_password("Pass123!"), estado="INACTIVO")
    db.add_all([admin, inactive])
    await db.commit()
    headers = await _get_auth_headers(admin.id)

    response = await client.patch(f"/api/users/{inactive.id}/activate", headers=headers)
    assert response.status_code == 200
    assert response.json()["estado"] == "ACTIVO"


async def test_activate_already_active_user(client: AsyncClient, db: AsyncSession):
    """PATCH /activate sobre usuario ya activo retorna 400."""
    admin = User(email="admin_act2@example.com", password_hash=hash_password("Admin123!"), estado="ACTIVO")
    active = User(email="alreadyactive@example.com", password_hash=hash_password("Pass123!"), estado="ACTIVO")
    db.add_all([admin, active])
    await db.commit()
    headers = await _get_auth_headers(admin.id)

    response = await client.patch(f"/api/users/{active.id}/activate", headers=headers)
    assert response.status_code == 400
    assert "ya está activo" in response.json()["detail"] or \
           "ya esta activo" in response.json()["detail"].lower()


async def test_activate_user_not_found(client: AsyncClient, db: AsyncSession):
    """PATCH /activate con ID inexistente retorna 404."""
    admin = User(email="admin_actnf@example.com", password_hash=hash_password("Admin123!"), estado="ACTIVO")
    db.add(admin)
    await db.commit()
    headers = await _get_auth_headers(admin.id)

    response = await client.patch(
        "/api/users/00000000-0000-0000-0000-000000000000/activate", headers=headers
    )
    assert response.status_code == 404


# ── Asignacion de roles a usuarios ───────────────────────────────────────────

async def test_assign_and_remove_role_from_user(client: AsyncClient, db: AsyncSession):
    """Asignar y remover un rol a un usuario correctamente."""
    admin = User(email="admin_roleassign@example.com", password_hash=hash_password("Admin123!"), estado="ACTIVO")
    user = User(email="roleuser@example.com", password_hash=hash_password("Pass123!"), estado="ACTIVO")
    role = Role(nombre="ROLE_ASSIGN_TEST", estado="ACTIVO")
    db.add_all([admin, user, role])
    await db.commit()
    headers = await _get_auth_headers(admin.id)

    # Asignar
    assign_resp = await client.post(
        f"/api/users/{user.id}/roles/{role.id}", headers=headers
    )
    assert assign_resp.status_code == 200

    # Remover
    remove_resp = await client.delete(
        f"/api/users/{user.id}/roles/{role.id}", headers=headers
    )
    assert remove_resp.status_code == 200


async def test_assign_role_user_not_found(client: AsyncClient, db: AsyncSession):
    """Asignar rol a usuario inexistente retorna 404."""
    admin = User(email="admin_rfnf@example.com", password_hash=hash_password("Admin123!"), estado="ACTIVO")
    role = Role(nombre="ROLE_NF_TEST", estado="ACTIVO")
    db.add_all([admin, role])
    await db.commit()
    headers = await _get_auth_headers(admin.id)

    response = await client.post(
        f"/api/users/00000000-0000-0000-0000-000000000000/roles/{role.id}", headers=headers
    )
    assert response.status_code == 404


async def test_remove_role_not_assigned(client: AsyncClient, db: AsyncSession):
    """Remover un rol que no estaba asignado retorna 400."""
    admin = User(email="admin_rna@example.com", password_hash=hash_password("Admin123!"), estado="ACTIVO")
    user = User(email="user_rna@example.com", password_hash=hash_password("Pass123!"), estado="ACTIVO")
    role = Role(nombre="ROLE_NOT_ASSIGNED", estado="ACTIVO")
    db.add_all([admin, user, role])
    await db.commit()
    headers = await _get_auth_headers(admin.id)

    response = await client.delete(
        f"/api/users/{user.id}/roles/{role.id}", headers=headers
    )
    assert response.status_code == 400
