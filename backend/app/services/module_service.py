# -*- coding: utf-8 -*-
"""
module_service.py — Servicio de lógica de negocio para la gestión de Módulos.
"""
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.module import Module
from app.schemas.module import ModuleCreate, ModuleUpdate


class ModuleService:
    @staticmethod
    async def get_by_id(db: AsyncSession, module_id: str) -> Optional[Module]:
        stmt = select(Module).where(Module.id == module_id, Module.estado == "ACTIVO")
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    @staticmethod
    async def list_active(db: AsyncSession, skip: int = 0, limit: int = 100) -> List[Module]:
        stmt = select(Module).where(Module.estado == "ACTIVO").offset(skip).limit(limit)
        result = await db.execute(stmt)
        return list(result.scalars().all())

    @staticmethod
    async def create(db: AsyncSession, obj_in: ModuleCreate, creator_id: Optional[str] = None) -> Module:
        db_obj = Module(
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
    async def update(db: AsyncSession, db_obj: Module, obj_in: ModuleUpdate, updater_id: Optional[str] = None) -> Module:
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
    async def delete(db: AsyncSession, db_obj: Module, updater_id: Optional[str] = None) -> Module:
        db_obj.soft_delete(updated_by=updater_id)
        db.add(db_obj)
        await db.flush()
        return db_obj
