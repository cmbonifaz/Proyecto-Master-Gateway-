# -*- coding: utf-8 -*-
"""
role.py — Schemas Pydantic para la gestión de Roles.
Sanitiza nombres y descripciones usando bleach (anti-XSS).
"""
import bleach
from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import datetime


class RoleBase(BaseModel):
    nombre: str = Field(..., max_length=100, pattern=r"^[A-Z_]+$")
    descripcion: Optional[str] = Field(None, max_length=500)

    @field_validator("nombre")
    @classmethod
    def sanitize_and_uppercase_nombre(cls, v: str) -> str:
        # Sanitizar y normalizar a mayúsculas
        cleaned = bleach.clean(v, tags=[], strip=True)
        return cleaned.upper()

    @field_validator("descripcion")
    @classmethod
    def sanitize_descripcion(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            return bleach.clean(v, tags=[], strip=True)
        return v


class RoleCreate(RoleBase):
    pass


class RoleUpdate(BaseModel):
    nombre: Optional[str] = Field(None, max_length=100, pattern=r"^[A-Z_]+$")
    descripcion: Optional[str] = Field(None, max_length=500)

    @field_validator("nombre")
    @classmethod
    def sanitize_and_uppercase_nombre(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            cleaned = bleach.clean(v, tags=[], strip=True)
            return cleaned.upper()
        return v

    @field_validator("descripcion")
    @classmethod
    def sanitize_descripcion(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            return bleach.clean(v, tags=[], strip=True)
        return v


class RoleResponse(RoleBase):
    id: str
    estado: str
    fecha_creacion: datetime
    fecha_actualizacion: datetime
    creado_por: Optional[str] = None
    actualizado_por: Optional[str] = None

    class Config:
        from_attributes = True
