# -*- coding: utf-8 -*-
"""
user_service.py — Servicio de lógica de negocio para Usuarios.
"""
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.user import User
from app.models.role import Role
from app.models.user_role import UserRole
from app.schemas.user import UserCreate, UserUpdate
from app.core.security import hash_password


class UserService:
    @staticmethod
    async def get_by_id(db: AsyncSession, user_id: str) -> Optional[User]:
        """
        Busca un usuario activo por su UUID.
        """
        stmt = select(User).where(User.id == user_id, User.estado == "ACTIVO")
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    @staticmethod
    async def get_any_by_id(db: AsyncSession, user_id: str) -> Optional[User]:
        """
        Busca un usuario por su UUID (activo o inactivo).
        """
        stmt = select(User).where(User.id == user_id)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    @staticmethod
    async def get_by_email(db: AsyncSession, email: str) -> Optional[User]:
        """
        Busca un usuario activo por su correo electrónico.
        """
        stmt = select(User).where(User.email == email, User.estado == "ACTIVO")
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    @staticmethod
    async def get_any_by_email(db: AsyncSession, email: str) -> Optional[User]:
        """
        Busca un usuario por su correo electrónico (activo o inactivo).
        """
        stmt = select(User).where(User.email == email)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    @staticmethod
    async def list_active(db: AsyncSession, skip: int = 0, limit: int = 100) -> List[User]:
        """
        Lista usuarios activos paginados.
        """
        stmt = select(User).where(User.estado == "ACTIVO").offset(skip).limit(limit)
        result = await db.execute(stmt)
        return list(result.scalars().all())

    @staticmethod
    async def list_all(db: AsyncSession, skip: int = 0, limit: int = 100) -> List[User]:
        """
        Lista todos los usuarios paginados (activos e inactivos).
        """
        stmt = select(User).offset(skip).limit(limit)
        result = await db.execute(stmt)
        return list(result.scalars().all())

    @staticmethod
    async def create(db: AsyncSession, obj_in: UserCreate, creator_id: Optional[str] = None) -> User:
        """
        Crea un nuevo usuario con contraseña cifrada (bcrypt).
        """
        db_obj = User(
            email=obj_in.email,
            nombre=obj_in.nombre,
            password_hash=hash_password(obj_in.password),
            creado_por=creator_id,
            actualizado_por=creator_id
        )
        db.add(db_obj)
        await db.flush()
        
        # Consultamos el usuario de nuevo para que se cargue la relación 'roles' (lazy="selectin")
        # y evitar un error de greenlet al serializar.
        stmt = select(User).where(User.id == db_obj.id)
        result = await db.execute(stmt)
        return result.scalar_one()

    @staticmethod
    async def update(db: AsyncSession, db_obj: User, obj_in: UserUpdate, updater_id: Optional[str] = None) -> User:
        """
        Actualiza los datos de un usuario. Si se incluye contraseña, se vuelve a cifrar.
        """
        if obj_in.email is not None:
            db_obj.email = obj_in.email
        if obj_in.nombre is not None:
            db_obj.nombre = obj_in.nombre
        if obj_in.password is not None:
            db_obj.password_hash = hash_password(obj_in.password)
        
        db_obj.actualizado_por = updater_id
        db.add(db_obj)
        await db.flush()
        
        # Consultamos el usuario de nuevo para recargar la relación y evitar que quede expirada tras el flush.
        stmt = select(User).where(User.id == db_obj.id)
        result = await db.execute(stmt)
        return result.scalar_one()

    @staticmethod
    async def delete(db: AsyncSession, user: User, updater_id: Optional[str] = None) -> User:
        """
        Soft delete: cambia el estado del usuario a INACTIVO.
        """
        user.estado = "INACTIVO"
        user.actualizado_por = updater_id
        db.add(user)
        await db.commit()
        await db.refresh(user)
        return user

    @staticmethod
    async def activate(db: AsyncSession, user: User, updater_id: Optional[str] = None) -> User:
        """
        Activa un usuario inactivo.
        """
        user.estado = "ACTIVO"
        user.actualizado_por = updater_id
        db.add(user)
        await db.commit()
        await db.refresh(user)
        return user
