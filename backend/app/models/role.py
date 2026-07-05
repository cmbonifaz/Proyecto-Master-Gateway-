# -*- coding: utf-8 -*-
"""
role.py — Modelo de dominio para Rol.
"""
from sqlalchemy import Column, String, Text
from sqlalchemy.orm import relationship
from app.models.base import BaseAudit


class Role(BaseAudit):
    __tablename__ = "roles"

    nombre = Column(
        String(100),
        nullable=False,
        unique=True,
        index=True,
        comment="Nombre del rol (ej: ADMIN, VENDEDOR)",
    )

    descripcion = Column(
        Text,
        nullable=True,
        comment="Descripción opcional del rol",
    )

    # Relación M:N con User
    users = relationship(
        "User",
        secondary="user_roles",
        back_populates="roles",
        lazy="selectin",
    )

    # Relación M:N con Module
    modules = relationship(
        "Module",
        secondary="role_modules",
        back_populates="roles",
        lazy="selectin",
    )

    # Relación M:N con Menu
    menus = relationship(
        "Menu",
        secondary="role_menus",
        back_populates="roles",
        lazy="selectin",
    )

    def __repr__(self):
        return f"<Role id={self.id} nombre={self.nombre} estado={self.estado}>"
