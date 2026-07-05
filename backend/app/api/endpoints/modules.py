# -*- coding: utf-8 -*-
"""
modules.py — Endpoints HTTP para la administración de Módulos del sistema.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.core.database import get_db
from app.core.dependencies import get_current_user, CurrentUser
from app.schemas.module import ModuleCreate, ModuleUpdate, ModuleResponse
from app.services.module_service import ModuleService

router = APIRouter()


@router.get("/", response_model=List[ModuleResponse], summary="Listar módulos activos")
async def list_modules(
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
):
    return await ModuleService.list_active(db, skip=skip, limit=limit)


@router.get("/{module_id}", response_model=ModuleResponse, summary="Obtener módulo por ID")
async def get_module(
    module_id: str,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db)
):
    module = await ModuleService.get_by_id(db, module_id)
    if not module:
        raise HTTPException(status_code=404, detail="Módulo no encontrado")
    return module


@router.post("/", response_model=ModuleResponse, status_code=status.HTTP_201_CREATED, summary="Crear un módulo")
async def create_module(
    obj_in: ModuleCreate,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db)
):
    creator_id = current_user["user"].id
    return await ModuleService.create(db, obj_in, creator_id=creator_id)


@router.put("/{module_id}", response_model=ModuleResponse, summary="Actualizar un módulo")
async def update_module(
    module_id: str,
    obj_in: ModuleUpdate,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db)
):
    module = await ModuleService.get_by_id(db, module_id)
    if not module:
        raise HTTPException(status_code=404, detail="Módulo no encontrado")
        
    updater_id = current_user["user"].id
    return await ModuleService.update(db, module, obj_in, updater_id=updater_id)


@router.delete("/{module_id}", response_model=ModuleResponse, summary="Eliminar un módulo (Soft Delete)")
async def delete_module(
    module_id: str,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db)
):
    module = await ModuleService.get_by_id(db, module_id)
    if not module:
        raise HTTPException(status_code=404, detail="Módulo no encontrado")
        
    updater_id = current_user["user"].id
    return await ModuleService.delete(db, module, updater_id=updater_id)
