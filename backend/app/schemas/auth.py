# -*- coding: utf-8 -*-
"""
auth.py — Schemas Pydantic para los flujos de autenticación y tokens.
"""
from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional


class LoginRequest(BaseModel):
    """
    Datos requeridos para el primer paso de login.
    """
    email: EmailStr = Field(
        ..., 
        description="Correo electrónico institucional o de usuario"
    )
    password: str = Field(
        ..., 
        min_length=8, 
        max_length=128, 
        description="Contraseña del usuario"
    )


class RoleOption(BaseModel):
    """
    Representa una opción de rol devuelta tras el login exitoso.
    """
    id: str
    nombre: str
    descripcion: Optional[str] = None


class TempTokenResponse(BaseModel):
    """
    Respuesta tras login exitoso (Paso 1).
    Contiene un token temporal y la lista de roles asignados.
    """
    temp_token: str = Field(
        ..., 
        description="Token de corta duración (5 min) para seleccionar rol"
    )
    roles: List[RoleOption] = Field(
        ..., 
        description="Lista de roles que el usuario puede elegir"
    )


class RoleSelectRequest(BaseModel):
    """
    Petición para el paso 2 de autenticación.
    """
    temp_token: str = Field(
        ..., 
        description="Token temporal obtenido del login"
    )
    role_id: str = Field(
        ..., 
        description="ID del rol seleccionado"
    )


class TokenResponse(BaseModel):
    """
    Respuesta con los tokens definitivos (Paso 2).
    """
    access_token: str = Field(..., description="JWT con permisos del rol")
    refresh_token: str = Field(..., description="Token para renovar el JWT")
    token_type: str = Field("bearer", description="Tipo de token")


class RefreshTokenRequest(BaseModel):
    """
    Petición para renovar el access token.
    """
    refresh_token: str = Field(..., description="Refresh token activo")


class TokenPayload(BaseModel):
    """
    Payload decodificado de los tokens.
    """
    sub: Optional[str] = None
    type: Optional[str] = None
    role_id: Optional[str] = None
    exp: Optional[int] = None
