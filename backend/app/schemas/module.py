# -*- coding: utf-8 -*-
"""
module.py — Schemas Pydantic para los Módulos de la aplicación.
Sanitiza campos con bleach (anti-XSS).
"""
import bleach
from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import datetime


class ModuleBase(BaseModel):
    nombre: str = Field(..., max_length=100)
    descripcion: Optional[str] = Field(None, max_length=500)

    @field_validator("nombre", "descripcion")
    @classmethod
    def sanitize_fields(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            return bleach.clean(v, tags=[], strip=True)
        return v


class ModuleCreate(ModuleBase):
    pass


class ModuleUpdate(BaseModel):
    nombre: Optional[str] = Field(None, max_length=100)
    descripcion: Optional[str] = Field(None, max_length=500)

    @field_validator("nombre", "descripcion")
    @classmethod
    def sanitize_fields(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            return bleach.clean(v, tags=[], strip=True)
        return v


class ModuleResponse(ModuleBase):
    id: str
    estado: str
    fecha_creacion: datetime
    fecha_actualizacion: datetime
    creado_por: Optional[str] = None
    actualizado_por: Optional[str] = None

    class Config:
        from_attributes = True
