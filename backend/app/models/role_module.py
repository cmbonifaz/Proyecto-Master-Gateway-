# -*- coding: utf-8 -*-
"""
role_module.py — Tabla pivote M:N entre Role y Module.
Vincula un módulo completo a un rol.
"""
import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from app.core.database import Base


def _uuid(): return str(uuid.uuid4())
def _now(): return datetime.now(timezone.utc)


class RoleModule(Base):
    __tablename__ = "role_modules"
    __table_args__ = (
        UniqueConstraint("role_id", "module_id", name="uq_role_module"),
    )

    id = Column(UUID(as_uuid=False), primary_key=True, default=_uuid)
    role_id = Column(UUID(as_uuid=False), ForeignKey("roles.id", ondelete="CASCADE"), nullable=False, index=True)
    module_id = Column(UUID(as_uuid=False), ForeignKey("modules.id", ondelete="CASCADE"), nullable=False, index=True)
    fecha_creacion = Column(DateTime(timezone=True), default=_now, nullable=False)
    creado_por = Column(UUID(as_uuid=False), nullable=True)
