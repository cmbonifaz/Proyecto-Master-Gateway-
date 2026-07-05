# -*- coding: utf-8 -*-
"""
base.py — Modelo base de auditoría (BaseAudit).
TODAS las entidades de la BD deben heredar de esta clase.

Campos obligatorios según PDF del proyecto:
  - id, estado, fecha_creacion, fecha_actualizacion, creado_por, actualizado_por

Principio: Soft Delete obligatorio — nunca DELETE físico.
"""
import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, Enum as SAEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import declarative_mixin, declared_attr
from sqlalchemy import event
from app.core.database import Base


def _uuid_default():
    return str(uuid.uuid4())


def _now():
    return datetime.now(timezone.utc)


@declarative_mixin
class AuditMixin:
    """
    Mixin que agrega los campos de auditoría obligatorios a cualquier modelo.
    Usar junto con Base para todos los modelos del proyecto.

    Hooks del ORM:
      - fecha_creacion se establece automáticamente en INSERT
      - fecha_actualizacion se actualiza automáticamente en cada UPDATE
    """

    @declared_attr
    def id(cls):
        return Column(
            UUID(as_uuid=False),
            primary_key=True,
            default=_uuid_default,
            nullable=False,
            comment="Identificador único UUID",
        )

    @declared_attr
    def estado(cls):
        return Column(
            SAEnum("ACTIVO", "INACTIVO", name="estado_enum"),
            nullable=False,
            default="ACTIVO",
            index=True,
            comment="Estado del registro. Soft Delete: INACTIVO en vez de DELETE.",
        )

    @declared_attr
    def fecha_creacion(cls):
        return Column(
            DateTime(timezone=True),
            nullable=False,
            default=_now,
            comment="Timestamp automático de creación (managed by ORM)",
        )

    @declared_attr
    def fecha_actualizacion(cls):
        return Column(
            DateTime(timezone=True),
            nullable=False,
            default=_now,
            onupdate=_now,
            comment="Timestamp automático de última modificación (managed by ORM)",
        )

    @declared_attr
    def creado_por(cls):
        return Column(
            UUID(as_uuid=False),
            nullable=True,
            comment="UUID del usuario que creó el registro (null si es auto-registro)",
        )

    @declared_attr
    def actualizado_por(cls):
        return Column(
            UUID(as_uuid=False),
            nullable=True,
            comment="UUID del usuario que modificó el registro por última vez",
        )

    def soft_delete(self, updated_by: str = None):
        """
        Realiza un Soft Delete: cambia estado a INACTIVO.
        NUNCA llamar a session.delete() directamente.
        """
        self.estado = "INACTIVO"
        if updated_by:
            self.actualizado_por = updated_by


class BaseAudit(Base, AuditMixin):
    """
    Clase base completa para todos los modelos del proyecto.
    Combina la declaración de SQLAlchemy con el mixin de auditoría.
    """
    __abstract__ = True
