# -*- coding: utf-8 -*-
"""
revoked_token.py — Tabla de lista negra de Refresh Tokens revocados.

Propósito (Logout / Revocación):
  Los JWT son stateless por naturaleza. Para implementar un logout real
  (sin esperar a que expire el access_token), se almacena el refresh_token
  revocado en esta tabla. En cada llamada a /refresh-token o /logout se
  verifica contra esta tabla.

Estrategia de limpieza:
  Los registros pueden ser eliminados físicamente cuando su fecha de
  expiración haya pasado (tarea periódica, cron, etc.).
"""
import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, Text
from sqlalchemy.dialects.postgresql import UUID
from app.core.database import Base


def _uuid():
    return str(uuid.uuid4())


def _now():
    return datetime.now(timezone.utc)


class RevokedToken(Base):
    __tablename__ = "revoked_tokens"

    id = Column(UUID(as_uuid=False), primary_key=True, default=_uuid)

    # El token completo (o su hash SHA-256 en una optimización futura)
    token = Column(Text, nullable=False, unique=True, index=True,
                   comment="Refresh Token revocado")

    user_id = Column(UUID(as_uuid=False), nullable=True,
                     comment="UUID del usuario que tenía este token")

    revoked_at = Column(DateTime(timezone=True), default=_now, nullable=False,
                        comment="Momento exacto en que fue revocado")

    def __repr__(self):
        return f"<RevokedToken user={self.user_id} revoked_at={self.revoked_at}>"
