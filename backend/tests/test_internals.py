# -*- coding: utf-8 -*-
"""
test_internals.py — Pruebas para el endpoint interno /internals/validate-token.
Verifica los flujos de Zero Trust: token valido, invalido, tipo incorrecto y usuario inexistente.
"""
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User
from app.core.security import hash_password, create_token

pytestmark = pytest.mark.asyncio


async def _make_user(db: AsyncSession, email: str, estado: str = "ACTIVO") -> User:
    user = User(
        email=email,
        password_hash=hash_password("Password123!"),
        nombre="Test User",
        estado=estado
    )
    db.add(user)
    await db.commit()
    return user


# ── Casos validos ─────────────────────────────────────────────────────────────

async def test_validate_token_valid(client: AsyncClient, db: AsyncSession):
    """Token valido con usuario activo: retorna valid=True con user_id y role_id."""
    user = await _make_user(db, "internal_valid@example.com")
    token = create_token(user.id, "access_token", {"role_id": "some-role-id"})

    response = await client.post(
        "/api/internals/validate-token",
        json={"token": token}
    )
    assert response.status_code == 200
    body = response.json()
    assert body["valid"] is True
    assert body["user_id"] == user.id
    assert body["role_id"] == "some-role-id"


# ── Casos invalidos ───────────────────────────────────────────────────────────

async def test_validate_token_invalid_signature(client: AsyncClient):
    """Token con firma invalida: retorna valid=False."""
    response = await client.post(
        "/api/internals/validate-token",
        json={"token": "header.payload.firma_invalida"}
    )
    assert response.status_code == 200
    assert response.json()["valid"] is False


async def test_validate_token_wrong_type(client: AsyncClient, db: AsyncSession):
    """Usar refresh_token donde se espera access_token: retorna valid=False."""
    user = await _make_user(db, "internal_wrongtype@example.com")
    # Crear un refresh_token (tipo incorrecto para validate-token)
    refresh = create_token(user.id, "refresh_token")

    response = await client.post(
        "/api/internals/validate-token",
        json={"token": refresh}
    )
    assert response.status_code == 200
    assert response.json()["valid"] is False


async def test_validate_token_user_not_found(client: AsyncClient):
    """Token valido pero el user_id no existe en la BD: retorna valid=False."""
    # UUID que no existe en la base de datos
    fake_user_id = "00000000-0000-0000-0000-000000000000"
    token = create_token(fake_user_id, "access_token", {"role_id": "any"})

    response = await client.post(
        "/api/internals/validate-token",
        json={"token": token}
    )
    assert response.status_code == 200
    assert response.json()["valid"] is False


async def test_validate_token_temp_token_rejected(client: AsyncClient, db: AsyncSession):
    """Usar temp_token donde se espera access_token: retorna valid=False."""
    user = await _make_user(db, "internal_temp@example.com")
    temp = create_token(user.id, "temp_token")

    response = await client.post(
        "/api/internals/validate-token",
        json={"token": temp}
    )
    assert response.status_code == 200
    assert response.json()["valid"] is False
