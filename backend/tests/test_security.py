# -*- coding: utf-8 -*-
"""
test_security.py — Pruebas unitarias para las utilidades criptograficas en core/security.py.
Cubre: hash_password, verify_password, create_token, decode_token, verify_token_type.
"""
import pytest
from jose import JWTError
from app.core.security import (
    hash_password,
    verify_password,
    create_token,
    decode_token,
    verify_token_type,
)

# Nota: estos tests son sincronos (no usan async/await ni BD)


# ── hash_password / verify_password ──────────────────────────────────────────

def test_hash_password_generates_bcrypt_hash():
    """El hash generado no es igual al texto plano."""
    plain = "MiPassword123!"
    hashed = hash_password(plain)
    assert hashed != plain
    assert hashed.startswith("$2b$") or hashed.startswith("$2a$")  # prefijo bcrypt


def test_hash_password_is_not_deterministic():
    """Dos hashes del mismo password son distintos (bcrypt usa salt aleatorio)."""
    plain = "MiPassword123!"
    hash1 = hash_password(plain)
    hash2 = hash_password(plain)
    assert hash1 != hash2


def test_verify_password_correct():
    """verify_password retorna True para el par correcto."""
    plain = "CorrectPass99!"
    hashed = hash_password(plain)
    assert verify_password(plain, hashed) is True


def test_verify_password_incorrect():
    """verify_password retorna False para password incorrecto."""
    hashed = hash_password("Original123!")
    assert verify_password("WrongPassword!", hashed) is False


def test_verify_password_empty_string():
    """verify_password retorna False para password vacio."""
    hashed = hash_password("Original123!")
    assert verify_password("", hashed) is False


# ── create_token / decode_token ───────────────────────────────────────────────

def test_create_and_decode_temp_token():
    """temp_token se crea y decodifica correctamente con tipo correcto."""
    subject = "user-uuid-001"
    token = create_token(subject, "temp_token")
    payload = decode_token(token)
    assert payload["sub"] == subject
    assert payload["type"] == "temp_token"
    assert "exp" in payload
    assert "iat" in payload


def test_create_and_decode_access_token():
    """access_token incluye los extra_claims (role_id)."""
    subject = "user-uuid-002"
    role_id = "role-uuid-abc"
    token = create_token(subject, "access_token", {"role_id": role_id})
    payload = decode_token(token)
    assert payload["sub"] == subject
    assert payload["type"] == "access_token"
    assert payload["role_id"] == role_id


def test_create_and_decode_refresh_token():
    """refresh_token se crea sin extra_claims y se decodifica correctamente."""
    subject = "user-uuid-003"
    token = create_token(subject, "refresh_token")
    payload = decode_token(token)
    assert payload["sub"] == subject
    assert payload["type"] == "refresh_token"


def test_decode_token_invalid_signature_raises():
    """Decodificar un token con firma manipulada lanza JWTError."""
    token = create_token("user-001", "access_token")
    # Alterar el ultimo caracter de la firma
    tampered = token[:-3] + "xxx"
    with pytest.raises(JWTError):
        decode_token(tampered)


def test_decode_token_malformed_raises():
    """Decodificar un string que no es JWT lanza JWTError."""
    with pytest.raises(JWTError):
        decode_token("esto.no.es.un.jwt.valido")


# ── verify_token_type ─────────────────────────────────────────────────────────

def test_verify_token_type_correct():
    """verify_token_type no lanza excepcion cuando el tipo coincide."""
    token = create_token("user-001", "access_token", {"role_id": "r1"})
    payload = verify_token_type(token, "access_token")
    assert payload["sub"] == "user-001"
    assert payload["type"] == "access_token"


def test_verify_token_type_incorrect_raises():
    """verify_token_type lanza JWTError cuando el tipo no coincide."""
    # Crear refresh_token pero verificar como access_token
    token = create_token("user-001", "refresh_token")
    with pytest.raises(JWTError):
        verify_token_type(token, "access_token")


def test_verify_token_type_temp_as_access_raises():
    """temp_token rechazado cuando se espera access_token."""
    token = create_token("user-001", "temp_token")
    with pytest.raises(JWTError):
        verify_token_type(token, "access_token")


def test_verify_token_type_access_as_refresh_raises():
    """access_token rechazado cuando se espera refresh_token."""
    token = create_token("user-001", "access_token")
    with pytest.raises(JWTError):
        verify_token_type(token, "refresh_token")
