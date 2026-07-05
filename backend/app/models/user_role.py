# -*- coding: utf-8 -*-
"""
user_role.py — Tabla pivote M:N entre User y Role.

IMPORTANTE: Esta NO es una tabla tonta.
Según el PDF, la tabla intermedia debe heredar los campos de auditoría
para saber CUÁNDO se otorgó o revocó un permiso a un usuario específico.
"""
import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, ForeignKey, Enum as SAEnum, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID


def _uuid():
    return str(uuid.uuid4())


def _now():
    return datetime.now(timezone.utc)


# Usamos Table directamente (no BaseAudit) para mayor control,
# pero incluimos todos los campos de auditoría manualmente.
from app.core.database import Base


class UserRole(Base):
    __tablename__ = "user_roles"
    __table_args__ = (
        UniqueConstraint("user_id", "role_id", name="uq_user_role"),
    )

    id = Column(UUID(as_uuid=False), primary_key=True, default=_uuid)

    user_id = Column(
        UUID(as_uuid=False),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    role_id = Column(
        UUID(as_uuid=False),
        ForeignKey("roles.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # ── Campos de auditoría propios (según PDF) ───────────────────────────────
    estado = Column(
        SAEnum("ACTIVO", "INACTIVO", name="estado_user_role_enum"),
        nullable=False,
        default="ACTIVO",
    )
    fecha_creacion = Column(DateTime(timezone=True), default=_now, nullable=False)
    fecha_actualizacion = Column(DateTime(timezone=True), default=_now, onupdate=_now, nullable=False)
    creado_por = Column(UUID(as_uuid=False), nullable=True)
    actualizado_por = Column(UUID(as_uuid=False), nullable=True)

    def __repr__(self):
        return f"<UserRole user={self.user_id} role={self.role_id} estado={self.estado}>"
