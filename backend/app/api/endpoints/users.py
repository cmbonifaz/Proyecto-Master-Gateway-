# -*- coding: utf-8 -*-
"""
users.py — Endpoints HTTP para la administración de Usuarios (CRUD).
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.core.database import get_db
from app.core.dependencies import get_current_user, CurrentUser
from app.schemas.user import UserCreate, UserUpdate, UserResponse
from app.services.user_service import UserService
from app.services.role_service import RoleService

router = APIRouter()


@router.get("/", response_model=List[UserResponse], summary="Listar usuarios activos")
async def list_users(
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
):
    # Por defecto, cualquier rol autenticado puede listar (se puede restringir a ADMIN)
    return await UserService.list_active(db, skip=skip, limit=limit)


@router.get("/{user_id}", response_model=UserResponse, summary="Obtener usuario por ID")
async def get_user(
    user_id: str,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db)
):
    user = await UserService.get_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return user


@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED, summary="Crear un usuario")
async def create_user(
    obj_in: UserCreate,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db)
):
    # Verificar si el email ya está en uso (activo o inactivo por restricciones de BD)
    existing = await UserService.get_any_by_email(db, obj_in.email)
    if existing:
        if existing.estado == "INACTIVO":
            raise HTTPException(
                status_code=400,
                detail="El correo electrónico ya existe en el sistema pero está INACTIVO. Contacte a soporte o use otro."
            )
        raise HTTPException(status_code=400, detail="El correo electrónico ya está registrado")
        
    creator_id = current_user["user"].id
    return await UserService.create(db, obj_in, creator_id=creator_id)


@router.put("/{user_id}", response_model=UserResponse, summary="Actualizar usuario")
async def update_user(
    user_id: str,
    obj_in: UserUpdate,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db)
):
    user = await UserService.get_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
        
    updater_id = current_user["user"].id
    return await UserService.update(db, user, obj_in, updater_id=updater_id)


@router.delete("/{user_id}", response_model=UserResponse, summary="Eliminar usuario (Soft Delete)")
async def delete_user(
    user_id: str,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db)
):
    user = await UserService.get_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
        
    # Impedir auto-eliminación por seguridad
    if user.id == current_user["user"].id:
        raise HTTPException(status_code=400, detail="No puedes auto-eliminarte de la plataforma")
        
    updater_id = current_user["user"].id
    return await UserService.delete(db, user, updater_id=updater_id)


# ── Asignación de Roles a Usuarios ──────────────────────────────────────────

@router.post("/{user_id}/roles/{role_id}", status_code=status.HTTP_200_OK, summary="Asignar rol a usuario")
async def assign_role(
    user_id: str,
    role_id: str,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db)
):
    # Verificar que el usuario y el rol existan
    user = await UserService.get_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
        
    role = await RoleService.get_by_id(db, role_id)
    if not role:
        raise HTTPException(status_code=404, detail="Rol no encontrado")
        
    creator_id = current_user["user"].id
    await RoleService.assign_role_to_user(db, user_id, role_id, creator_id=creator_id)
    return {"detail": "Rol asignado correctamente"}


@router.delete("/{user_id}/roles/{role_id}", status_code=status.HTTP_200_OK, summary="Remover rol de usuario")
async def remove_role(
    user_id: str,
    role_id: str,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db)
):
    user = await UserService.get_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
        
    role = await RoleService.get_by_id(db, role_id)
    if not role:
        raise HTTPException(status_code=404, detail="Rol no encontrado")
        
    updater_id = current_user["user"].id
    res = await RoleService.remove_role_from_user(db, user_id, role_id, updater_id=updater_id)
    if not res:
        raise HTTPException(status_code=400, detail="El rol no estaba asignado a este usuario")
        
    return {"detail": "Rol removido correctamente"}
