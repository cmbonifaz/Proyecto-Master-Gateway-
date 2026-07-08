# -*- coding: utf-8 -*-
"""
role_service.py — Servicio de lógica de negocio para la gestión de Roles y asignación a Usuarios.
"""
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from app.models.role import Role
from app.models.user_role import UserRole
from app.models.role_module import RoleModule
from app.models.role_menu import RoleMenu
from app.schemas.role import RoleCreate, RoleUpdate


class RoleService:
    @staticmethod
    async def get_by_id(db: AsyncSession, role_id: str) -> Optional[Role]:
        stmt = select(Role).where(Role.id == role_id, Role.estado == "ACTIVO")
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    @staticmethod
    async def get_by_nombre(db: AsyncSession, nombre: str) -> Optional[Role]:
        stmt = select(Role).where(Role.nombre == nombre, Role.estado == "ACTIVO")
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    @staticmethod
    async def list_active(db: AsyncSession, skip: int = 0, limit: int = 100) -> List[Role]:
        stmt = select(Role).where(Role.estado == "ACTIVO").offset(skip).limit(limit)
        result = await db.execute(stmt)
        return list(result.scalars().all())

    @staticmethod
    async def create(db: AsyncSession, obj_in: RoleCreate, creator_id: Optional[str] = None) -> Role:
        db_obj = Role(
            nombre=obj_in.nombre,
            descripcion=obj_in.descripcion,
            creado_por=creator_id,
            actualizado_por=creator_id
        )
        db.add(db_obj)
        await db.flush()
        await db.refresh(db_obj)
        return db_obj

    @staticmethod
    async def update(db: AsyncSession, db_obj: Role, obj_in: RoleUpdate, updater_id: Optional[str] = None) -> Role:
        if obj_in.nombre is not None:
            db_obj.nombre = obj_in.nombre
        if obj_in.descripcion is not None:
            db_obj.descripcion = obj_in.descripcion

        db_obj.actualizado_por = updater_id
        db.add(db_obj)
        await db.flush()
        await db.refresh(db_obj)
        return db_obj

    @staticmethod
    async def has_active_users(db: AsyncSession, role_id: str) -> bool:
        """
        Verifica si el rol tiene usuarios activos asignados.
        Usado para prevenir la eliminación de roles en uso.
        """
        stmt = select(UserRole).where(
            and_(UserRole.role_id == role_id, UserRole.estado == "ACTIVO")
        ).limit(1)
        result = await db.execute(stmt)
        return result.scalar_one_or_none() is not None

    @staticmethod
    async def delete(db: AsyncSession, db_obj: Role, updater_id: Optional[str] = None) -> Role:
        """
        Soft delete del rol.
        """
        db_obj.soft_delete(updated_by=updater_id)
        db.add(db_obj)
        await db.flush()
        return db_obj

    # ── Asignación de Roles a Usuarios ──────────────────────────────────────────
    @staticmethod
    async def assign_role_to_user(
        db: AsyncSession,
        user_id: str,
        role_id: str,
        creator_id: Optional[str] = None
    ) -> UserRole:
        """
        Asigna un rol a un usuario creando un registro en la tabla pivote user_roles.
        Si ya existe e indica estado INACTIVO (soft delete anterior), lo activa.
        """
        stmt = select(UserRole).where(
            and_(UserRole.user_id == user_id, UserRole.role_id == role_id)
        )
        result = await db.execute(stmt)
        user_role = result.scalar_one_or_none()

        if user_role:
            user_role.estado = "ACTIVO"
            user_role.actualizado_por = creator_id
        else:
            user_role = UserRole(
                user_id=user_id,
                role_id=role_id,
                creado_por=creator_id,
                actualizado_por=creator_id
            )
            db.add(user_role)

        await db.flush()
        return user_role

    @staticmethod
    async def remove_role_from_user(
        db: AsyncSession,
        user_id: str,
        role_id: str,
        updater_id: Optional[str] = None
    ) -> Optional[UserRole]:
        """
        Soft delete de la asociación de rol del usuario en la tabla pivote.
        """
        stmt = select(UserRole).where(
            and_(UserRole.user_id == user_id, UserRole.role_id == role_id, UserRole.estado == "ACTIVO")
        )
        result = await db.execute(stmt)
        user_role = result.scalar_one_or_none()

        if user_role:
            user_role.estado = "INACTIVO"
            user_role.actualizado_por = updater_id
            db.add(user_role)
            await db.flush()

        return user_role

    # ── Asignación de Módulos a Roles ─────────────────────────────────────────
    @staticmethod
    async def assign_module_to_role(
        db: AsyncSession,
        role_id: str,
        module_id: str,
        creator_id: Optional[str] = None
    ) -> RoleModule:
        """
        Vincula un módulo completo a un rol (M:N).
        Si ya existe la relación, la retorna sin duplicar.
        """
        stmt = select(RoleModule).where(
            and_(RoleModule.role_id == role_id, RoleModule.module_id == module_id)
        )
        result = await db.execute(stmt)
        role_module = result.scalar_one_or_none()

        if not role_module:
            role_module = RoleModule(
                role_id=role_id,
                module_id=module_id,
                creado_por=creator_id
            )
            db.add(role_module)
            await db.flush()

        return role_module

    @staticmethod
    async def remove_module_from_role(
        db: AsyncSession,
        role_id: str,
        module_id: str
    ) -> Optional[RoleModule]:
        """
        Elimina físicamente la relación entre un rol y un módulo (DELETE físico de la tabla pivote).
        """
        stmt = select(RoleModule).where(
            and_(RoleModule.role_id == role_id, RoleModule.module_id == module_id)
        )
        result = await db.execute(stmt)
        role_module = result.scalar_one_or_none()

        if role_module:
            await db.delete(role_module)
            await db.flush()

        return role_module

    # ── Asignación de Menús a Roles ────────────────────────────────────────────
    @staticmethod
    async def assign_menu_to_role(
        db: AsyncSession,
        role_id: str,
        menu_id: str,
        creator_id: Optional[str] = None
    ) -> RoleMenu:
        """
        Asigna un ítem/submenú específico a un rol (M:N).
        Si ya existe la relación, la retorna sin duplicar.
        """
        stmt = select(RoleMenu).where(
            and_(RoleMenu.role_id == role_id, RoleMenu.menu_id == menu_id)
        )
        result = await db.execute(stmt)
        role_menu = result.scalar_one_or_none()

        if not role_menu:
            role_menu = RoleMenu(
                role_id=role_id,
                menu_id=menu_id,
                creado_por=creator_id
            )
            db.add(role_menu)
            await db.flush()

        return role_menu

    @staticmethod
    async def remove_menu_from_role(
        db: AsyncSession,
        role_id: str,
        menu_id: str
    ) -> Optional[RoleMenu]:
        """
        Elimina físicamente la relación entre un rol y un menú (DELETE físico de la tabla pivote).
        """
        stmt = select(RoleMenu).where(
            and_(RoleMenu.role_id == role_id, RoleMenu.menu_id == menu_id)
        )
        result = await db.execute(stmt)
        role_menu = result.scalar_one_or_none()

        if role_menu:
            await db.delete(role_menu)
            await db.flush()

        return role_menu
