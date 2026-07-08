# -*- coding: utf-8 -*-
"""
Paquete models — Importar todos los modelos aquí para que Alembic los detecte.
El orden de importación respeta las dependencias entre tablas.
"""
from app.models.base import BaseAudit          # noqa: F401
from app.models.user import User               # noqa: F401
from app.models.role import Role               # noqa: F401
from app.models.module import Module           # noqa: F401
from app.models.menu import Menu               # noqa: F401
from app.models.user_role import UserRole      # noqa: F401
from app.models.role_module import RoleModule  # noqa: F401
from app.models.role_menu import RoleMenu      # noqa: F401
from app.models.revoked_token import RevokedToken  # noqa: F401
