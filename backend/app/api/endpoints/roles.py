# -*- coding: utf-8 -*-
"""
roles.py — Endpoints HTTP para la administración de Roles.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.core.database import get_db
from app.core.dependencies import get_current_user, CurrentUser
from app.schemas.role import RoleCreate, RoleUpdate, RoleResponse
from app.services.role_service import RoleService

router = APIRouter()


@router.get("/", response_model=List[RoleResponse], summary="Listar roles activos")
async def list_roles(
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    #Para la version 1 no se implementan busquedas por filtros 
):
    return await RoleService.list_active(db, skip=skip, limit=limit)


@router.get("/{role_id}", response_model=RoleResponse, summary="Obtener rol por ID")
async def get_role(
    role_id: str,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db)
):
    role = await RoleService.get_by_id(db, role_id)
    if not role:
        raise HTTPException(status_code=404, detail="Rol no encontrado")
    return role


@router.post("/", response_model=RoleResponse, status_code=status.HTTP_201_CREATED, summary="Crear un rol")
async def create_role(
    obj_in: RoleCreate,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db)
):
    existing = await RoleService.get_by_nombre(db, obj_in.nombre)
    if existing:
        raise HTTPException(status_code=400, detail="Ya existe un rol con ese nombre")
        
    creator_id = current_user["user"].id
    return await RoleService.create(db, obj_in, creator_id=creator_id)


@router.put("/{role_id}", response_model=RoleResponse, summary="Actualizar un rol")
async def update_role(
    role_id: str,
    obj_in: RoleUpdate,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db)
):
    role = await RoleService.get_by_id(db, role_id)
    if not role:
        raise HTTPException(status_code=404, detail="Rol no encontrado")
        
    updater_id = current_user["user"].id
    return await RoleService.update(db, role, obj_in, updater_id=updater_id)


@router.delete("/{role_id}", response_model=RoleResponse, summary="Eliminar un rol (Soft Delete)")
async def delete_role(
    role_id: str,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db)
):
    role = await RoleService.get_by_id(db, role_id)
    if not role:
        raise HTTPException(status_code=404, detail="Rol no encontrado")
        
    # Validaciones Shift-Left: Prevenir borrar ADMIN
    if role.nombre == "ADMIN":
        raise HTTPException(status_code=400, detail="El rol ADMINISTRADOR del sistema es vital y no se puede eliminar")
        
    updater_id = current_user["user"].id
    return await RoleService.delete(db, role, updater_id=updater_id)
