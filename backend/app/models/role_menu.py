# -*- coding: utf-8 -*-
"""
role_menu.py — Tabla pivote M:N entre Role y Menu.
Asigna un ítem/submenú específico a un rol.
"""
import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from app.core.database import Base


def _uuid(): return str(uuid.uuid4())
def _now(): return datetime.now(timezone.utc)


class RoleMenu(Base):
    __tablename__ = "role_menus"
    __table_args__ = (
        UniqueConstraint("role_id", "menu_id", name="uq_role_menu"),
    )

    id = Column(UUID(as_uuid=False), primary_key=True, default=_uuid)
    role_id = Column(UUID(as_uuid=False), ForeignKey("roles.id", ondelete="CASCADE"), nullable=False, index=True)
    menu_id = Column(UUID(as_uuid=False), ForeignKey("menus.id", ondelete="CASCADE"), nullable=False, index=True)
    fecha_creacion = Column(DateTime(timezone=True), default=_now, nullable=False)
    creado_por = Column(UUID(as_uuid=False), nullable=True)
