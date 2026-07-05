# -*- coding: utf-8 -*-
"""
module.py — Modelo de dominio para Módulo.
Los módulos son agrupadores administrativos de alto nivel (ej: "Ventas", "RRHH").
Al inactivar un módulo, sus menús asociados no deben renderizarse (lógica de frontend).
"""
from sqlalchemy import Column, String, Text
from sqlalchemy.orm import relationship
from app.models.base import BaseAudit


class Module(BaseAudit):
    __tablename__ = "modules"

    nombre = Column(
        String(100),
        nullable=False,
        unique=True,
        index=True,
        comment="Nombre del módulo administrativo (ej: Ventas, RRHH)",
    )

    descripcion = Column(
        Text,
        nullable=True,
        comment="Descripción opcional del módulo",
    )

    # Relación M:N con Role
    roles = relationship(
        "Role",
        secondary="role_modules",
        back_populates="modules",
        lazy="selectin",
    )

    def __repr__(self):
        return f"<Module id={self.id} nombre={self.nombre} estado={self.estado}>"
