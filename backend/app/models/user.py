# -*- coding: utf-8 -*-
"""
user.py — Modelo de dominio para Usuario.
"""
from sqlalchemy import Column, String
from sqlalchemy.orm import relationship
from app.models.base import BaseAudit


class User(BaseAudit):
    __tablename__ = "users"

    email = Column(
        String(255),
        nullable=False,
        unique=True,
        index=True,
        comment="Email único del usuario (usado como login)",
    )

    # Hash bcrypt — NUNCA se devuelve en responses (serialización ORM lo excluye)
    password_hash = Column(
        String(255),
        nullable=False,
        comment="Hash bcrypt de la contraseña. NUNCA exponer en API.",
    )

    nombre = Column(String(100), nullable=True, comment="Nombre completo del usuario")

    # Relación M:N con Role a través de la tabla pivote user_roles
    roles = relationship(
        "Role",
        secondary="user_roles",
        back_populates="users",
        lazy="selectin",
    )

    def __repr__(self):
        return f"<User id={self.id} email={self.email} estado={self.estado}>"
