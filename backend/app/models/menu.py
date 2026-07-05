# -*- coding: utf-8 -*-
"""
menu.py — Modelo de dominio para Menú (Patrón Adjacency List).

Estructura jerárquica recursiva:
  - Un Menu puede tener un parent_id (otro Menu) → submenu
  - Si parent_id es NULL → es raíz (módulo/sección principal)
  - Si url es NULL → es un contenedor/padre (no navegable directamente)
  - Si url NO es NULL → es un item hoja (navegable)

El árbol completo se obtiene con WITH RECURSIVE en PostgreSQL.
"""
from sqlalchemy import Column, String, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.models.base import BaseAudit


class Menu(BaseAudit):
    __tablename__ = "menus"

    texto = Column(
        String(150),
        nullable=False,
        comment="Texto visible del ítem en la UI (ej: 'Gestión de Usuarios')",
    )

    url = Column(
        String(500),
        nullable=True,
        comment="Ruta de navegación. NULL si es un contenedor padre (no hoja).",
    )

    icono = Column(
        String(100),
        nullable=True,
        comment="Clase de ícono CSS (ej: 'fas fa-users') para el frontend",
    )

    orden = Column(
        String(10),
        nullable=True,
        comment="Orden de renderizado entre ítems del mismo nivel (ej: '001', '002')",
    )

    # ── Adjacency List (autorreferencia) ──────────────────────────────────────
    parent_id = Column(
        UUID(as_uuid=False),
        ForeignKey("menus.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
        comment="UUID del menú padre. NULL si es elemento raíz.",
    )

    # Hijos directos del nodo (lazy='selectin' para evitar N+1 en árbol pequeño)
    children = relationship(
        "Menu",
        backref="parent",
        foreign_keys=[parent_id],
        lazy="selectin",
    )

    # Relación M:N con Role
    roles = relationship(
        "Role",
        secondary="role_menus",
        back_populates="menus",
        lazy="selectin",
    )

    def __repr__(self):
        return (
            f"<Menu id={self.id} texto='{self.texto}' "
            f"parent_id={self.parent_id} estado={self.estado}>"
        )
