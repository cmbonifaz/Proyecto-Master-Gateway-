# -*- coding: utf-8 -*-
"""
user.py — Schemas Pydantic para la gestión de Usuarios.
Incluye validación estricta de contraseñas y sanitización de nombres con bleach (anti-XSS).
"""
import bleach
import re
from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import List, Optional
from datetime import datetime


class UserBase(BaseModel):
    email: EmailStr = Field(..., max_length=255)
    nombre: Optional[str] = Field(None, max_length=100)

    @field_validator("nombre")
    @classmethod
    def sanitize_nombre(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            # Sanitización Shift-Left para evitar XSS almacenado
            cleaned = bleach.clean(v, tags=[], strip=True)
            return cleaned
        return v


class UserCreate(UserBase):
    password: str = Field(..., min_length=8, max_length=128)

    @field_validator("password")
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        # Validación de contraseña fuerte
        if not re.search(r"[A-Z]", v):
            raise ValueError("La contraseña debe incluir al menos una letra mayúscula.")
        if not re.search(r"[a-z]", v):
            raise ValueError("La contraseña debe incluir al menos una letra minúscula.")
        if not re.search(r"[0-9]", v):
            raise ValueError("La contraseña debe incluir al menos un número.")
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", v):
            raise ValueError("La contraseña debe incluir al menos un carácter especial.")
        return v


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = Field(None, max_length=255)
    nombre: Optional[str] = Field(None, max_length=100)
    password: Optional[str] = Field(None, min_length=8, max_length=128)

    @field_validator("nombre")
    @classmethod
    def sanitize_nombre(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            return bleach.clean(v, tags=[], strip=True)
        return v

    @field_validator("password")
    @classmethod
    def validate_password_strength(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            if not re.search(r"[A-Z]", v):
                raise ValueError("La contraseña debe incluir al menos una letra mayúscula.")
            if not re.search(r"[a-z]", v):
                raise ValueError("La contraseña debe incluir al menos una letra minúscula.")
            if not re.search(r"[0-9]", v):
                raise ValueError("La contraseña debe incluir al menos un número.")
            if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", v):
                raise ValueError("La contraseña debe incluir al menos un carácter especial.")
        return v


class RoleSummary(BaseModel):
    id: str
    nombre: str

    class Config:
        from_attributes = True


class UserResponse(UserBase):
    id: str
    estado: str
    fecha_creacion: datetime
    fecha_actualizacion: datetime
    creado_por: Optional[str] = None
    actualizado_por: Optional[str] = None
    roles: List[RoleSummary] = []

    class Config:
        from_attributes = True
