# -*- coding: utf-8 -*-
"""
menu.py — Schemas Pydantic para los Menús recursivos.
Incluye el soporte para la estructura jerárquica de árbol.
"""
import bleach
from pydantic import BaseModel, Field, field_validator
from typing import List, Optional
from datetime import datetime


class MenuBase(BaseModel):
    texto: str = Field(..., max_length=150, description="Etiqueta visible del menú")
    url: Optional[str] = Field(None, max_length=500, description="Ruta de navegación")
    icono: Optional[str] = Field(None, max_length=100, description="Clase de ícono CSS")
    orden: Optional[str] = Field(None, max_length=10, description="Orden numérico o string (ej. '001')")
    parent_id: Optional[str] = Field(None, description="UUID del menú padre, si aplica")

    @field_validator("texto", "url", "icono", "orden")
    @classmethod
    def sanitize_fields(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            return bleach.clean(v, tags=[], strip=True)
        return v


class MenuCreate(MenuBase):
    pass


class MenuUpdate(BaseModel):
    texto: Optional[str] = Field(None, max_length=150)
    url: Optional[str] = Field(None, max_length=500)
    icono: Optional[str] = Field(None, max_length=100)
    orden: Optional[str] = Field(None, max_length=10)
    parent_id: Optional[str] = Field(None)

    @field_validator("texto", "url", "icono", "orden")
    @classmethod
    def sanitize_fields(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            return bleach.clean(v, tags=[], strip=True)
        return v


class MenuResponse(MenuBase):
    id: str
    estado: str
    fecha_creacion: datetime
    fecha_actualizacion: datetime
    creado_por: Optional[str] = None
    actualizado_por: Optional[str] = None

    class Config:
        from_attributes = True


# Para la estructura de árbol recursiva
class MenuNode(BaseModel):
    id: str
    texto: str
    url: Optional[str] = None
    icono: Optional[str] = None
    orden: Optional[str] = None
    parent_id: Optional[str] = None
    children: List["MenuNode"] = []

    class Config:
        from_attributes = True
