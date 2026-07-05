# -*- coding: utf-8 -*-
"""
auth_service.py — Servicio de lógica de negocio para la autenticación de doble paso (Zero Trust).
"""
from typing import Optional, Tuple, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from jose import JWTError

from app.models.user import User
from app.models.role import Role
from app.models.user_role import UserRole
from app.core.security import verify_password, create_token, verify_token_type
from app.schemas.auth import LoginRequest, RoleOption, TempTokenResponse, TokenResponse


class AuthService:
    @staticmethod
    async def authenticate_user(db: AsyncSession, obj_in: LoginRequest) -> Optional[User]:
        """
        Paso 1: Valida el correo y la contraseña.
        Devuelve el objeto User si es correcto, None en caso contrario.
        """
        stmt = select(User).where(User.email == obj_in.email, User.estado == "ACTIVO")
        result = await db.execute(stmt)
        user = result.scalar_one_or_none()

        if not user:
            return None

        if not verify_password(obj_in.password, user.password_hash):
            return None

        return user

    @staticmethod
    async def get_user_roles(db: AsyncSession, user_id: str) -> List[RoleOption]:
        """
        Paso 1: Obtiene la lista de roles activos asociados al usuario.
        """
        stmt = (
            select(Role)
            .join(UserRole, Role.id == UserRole.role_id)
            .where(
                and_(
                    UserRole.user_id == user_id,
                    UserRole.estado == "ACTIVO",
                    Role.estado == "ACTIVO"
                )
            )
        )
        result = await db.execute(stmt)
        roles = result.scalars().all()
        return [RoleOption(id=r.id, nombre=r.nombre, descripcion=r.descripcion) for r in roles]

    @classmethod
    async def login_step1(db: AsyncSession, obj_in: LoginRequest) -> Optional[TempTokenResponse]:
        """
        Ejecuta el Paso 1 de Login.
        Retorna el token temporal (5 minutos de expiración) y las opciones de roles.
        """
        user = await db.execute(
            select(User).where(User.email == obj_in.email, User.estado == "ACTIVO")
        )
        user_obj = user.scalar_one_or_none()
        
        if not user_obj or not verify_password(obj_in.password, user_obj.password_hash):
            return None

        roles = await AuthService.get_user_roles(db, user_obj.id)
        if not roles:
            return None

        # Crea un TempToken firmado de corta duración
        temp_token = create_token(
            subject=user_obj.id,
            token_type="temp_token"
        )
        return TempTokenResponse(temp_token=temp_token, roles=roles)

    @classmethod
    async def select_role_step2(
        db: AsyncSession, 
        temp_token: str, 
        role_id: str
    ) -> Optional[TokenResponse]:
        """
        Paso 2: Recibe el token temporal y el rol seleccionado.
        Valida que el usuario tenga ese rol activo, y genera el JWT final y Refresh Token.
        """
        try:
            payload = verify_token_type(temp_token, "temp_token")
            user_id = payload.get("sub")
        except JWTError:
            return None  # Token inválido o expirado

        # Validar relación User-Role activa
        stmt = select(UserRole).where(
            and_(
                UserRole.user_id == user_id,
                UserRole.role_id == role_id,
                UserRole.estado == "ACTIVO"
            )
        )
        res = await db.execute(stmt)
        user_role = res.scalar_one_or_none()

        if not user_role:
            return None  # Rol no asignado o inactivo

        # Generar JWT definitivo que incluye el role_id (Principle of Least Privilege)
        access_token = create_token(
            subject=user_id,
            token_type="access_token",
            extra_claims={"role_id": role_id}
        )

        refresh_token = create_token(
            subject=user_id,
            token_type="refresh_token"
        )

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token
        )

    @classmethod
    async def refresh_access_token(
        db: AsyncSession, 
        refresh_token: str,
        active_role_id: str  # Enviado por cliente o almacenado
    ) -> Optional[TokenResponse]:
        """
        Renueva un Access Token utilizando un Refresh Token válido.
        """
        try:
            payload = verify_token_type(refresh_token, "refresh_token")
            user_id = payload.get("sub")
        except JWTError:
            return None

        # Validar que el rol sigue activo para el usuario
        stmt = select(UserRole).where(
            and_(
                UserRole.user_id == user_id,
                UserRole.role_id == active_role_id,
                UserRole.estado == "ACTIVO"
            )
        )
        res = await db.execute(stmt)
        user_role = res.scalar_one_or_none()

        if not user_role:
            return None

        new_access = create_token(
            subject=user_id,
            token_type="access_token",
            extra_claims={"role_id": active_role_id}
        )
        new_refresh = create_token(
            subject=user_id,
            token_type="refresh_token"
        )

        return TokenResponse(
            access_token=new_access,
            refresh_token=new_refresh
        )
