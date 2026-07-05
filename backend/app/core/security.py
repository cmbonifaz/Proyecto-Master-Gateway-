# -*- coding: utf-8 -*-
"""
security.py — Utilidades de seguridad centralizadas.
Maneja: hash de contraseñas (bcrypt), creación y verificación de JWT.

Principio Shift-Left: toda la lógica criptográfica está aquí,
no dispersa en los servicios.
"""
from datetime import datetime, timedelta, timezone
from typing import Optional, Literal
from jose import JWTError, jwt
from passlib.context import CryptContext
from app.core.config import settings

# ── Contexto de hashing (bcrypt) ───────────────────────────────────────────────
# bcrypt con alto cost factor (BCRYPT_ROUNDS=12) — resistente a fuerza bruta
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    bcrypt__rounds=settings.BCRYPT_ROUNDS,
)


# ── Funciones de Password ──────────────────────────────────────────────────────

def hash_password(plain_password: str) -> str:
    """
    Genera un hash bcrypt de la contraseña en texto plano.
    NUNCA almacenar contraseñas en texto plano.
    """
    return pwd_context.hash(plain_password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifica si una contraseña en texto plano coincide con su hash.
    Retorna False silenciosamente si no coincide (sin revelar detalles).
    """
    return pwd_context.verify(plain_password, hashed_password)


# ── Funciones de JWT ───────────────────────────────────────────────────────────

TokenType = Literal["temp_token", "access_token", "refresh_token"]


def create_token(
    subject: str,
    token_type: TokenType,
    extra_claims: Optional[dict] = None,
) -> str:
    """
    Crea un JWT firmado con el secreto de la aplicación.

    Args:
        subject:     Identificador del usuario (UUID como string).
        token_type:  Tipo de token — controla el tiempo de expiración.
        extra_claims: Claims adicionales (ej. role_id para access_token).

    Returns:
        JWT firmado como string.
    """
    now = datetime.now(timezone.utc)

    if token_type == "temp_token":
        expire = now + timedelta(minutes=settings.TEMP_TOKEN_EXPIRE_MINUTES)
    elif token_type == "access_token":
        expire = now + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    elif token_type == "refresh_token":
        expire = now + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)

    payload = {
        "sub": subject,        # Subject (user UUID)
        "type": token_type,    # Tipo de token (para validar contexto de uso)
        "iat": now,            # Issued at
        "exp": expire,         # Expiration
    }

    if extra_claims:
        payload.update(extra_claims)

    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)


def decode_token(token: str) -> dict:
    """
    Decodifica y valida un JWT.

    Raises:
        JWTError: Si el token es inválido, expirado o mal formado.

    Returns:
        Dict con los claims del payload.
    """
    return jwt.decode(
        token,
        settings.JWT_SECRET,
        algorithms=[settings.JWT_ALGORITHM],
    )


def verify_token_type(token: str, expected_type: TokenType) -> dict:
    """
    Decodifica el token y verifica que sea del tipo esperado.
    Previene que un TempToken sea usado como AccessToken (Zero Trust).

    Raises:
        JWTError: Si el tipo no coincide o el token es inválido.
    """
    payload = decode_token(token)
    if payload.get("type") != expected_type:
        raise JWTError(f"Token inválido: se esperaba '{expected_type}'")
    return payload
