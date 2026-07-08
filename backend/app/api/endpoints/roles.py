# -*- coding: utf-8 -*-
"""
roles.py — Endpoints HTTP para la administración de Roles.
Incluye: CRUD de roles + asignación de usuarios, módulos y menús a roles.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.core.database import get_db
from app.core.dependencies import get_current_user, CurrentUser
from app.schemas.role import RoleCreate, RoleUpdate, RoleResponse
from app.services.role_service import RoleService
from app.services.user_service import UserService
from app.services.module_service import ModuleService
from app.services.menu_service import MenuService

router = APIRouter()


# ── CRUD de Roles ──────────────────────────────────────────────────────────────

@router.get("/", response_model=List[RoleResponse], summary="Listar roles activos")
async def list_roles(
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
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

    # Shift-Left: Prevenir borrar el rol de ADMINISTRADOR del sistema
    if role.nombre == "ADMIN":
        raise HTTPException(
            status_code=400,
            detail="El rol ADMINISTRADOR del sistema es vital y no se puede eliminar"
        )

    # Prevenir eliminación de roles con usuarios activos asignados
    if await RoleService.has_active_users(db, role_id):
        raise HTTPException(
            status_code=400,
            detail="No se puede eliminar el rol porque tiene usuarios activos asignados. "
                   "Desasigne primero a todos los usuarios de este rol."
        )

    updater_id = current_user["user"].id
    return await RoleService.delete(db, role, updater_id=updater_id)


# ── Asignación de Usuarios a Roles ────────────────────────────────────────────

@router.post(
    "/{role_id}/users",
    status_code=status.HTTP_200_OK,
    summary="Asignar un usuario a este rol (M:N)"
)
async def assign_user_to_role(
    role_id: str,
    user_id: str,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db)
):
    """
    Asocia un usuario existente a este rol.
    Registra en la tabla pivote con sus propios campos de auditoría.
    """
    role = await RoleService.get_by_id(db, role_id)
    if not role:
        raise HTTPException(status_code=404, detail="Rol no encontrado")

    user = await UserService.get_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    creator_id = current_user["user"].id
    await RoleService.assign_role_to_user(db, user_id, role_id, creator_id=creator_id)
    return {"detail": f"Usuario '{user.email}' asignado al rol '{role.nombre}' correctamente"}


@router.delete(
    "/{role_id}/users/{user_id}",
    status_code=status.HTTP_200_OK,
    summary="Desasignar un usuario de este rol"
)
async def remove_user_from_role(
    role_id: str,
    user_id: str,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db)
):
    """
    Rompe la relación M:N entre el usuario y el rol (Soft Delete en tabla pivote).
    """
    role = await RoleService.get_by_id(db, role_id)
    if not role:
        raise HTTPException(status_code=404, detail="Rol no encontrado")

    user = await UserService.get_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    updater_id = current_user["user"].id
    res = await RoleService.remove_role_from_user(db, user_id, role_id, updater_id=updater_id)
    if not res:
        raise HTTPException(status_code=400, detail="El usuario no estaba asignado a este rol")

    return {"detail": f"Usuario '{user.email}' desasignado del rol '{role.nombre}' correctamente"}


# ── Asignación de Módulos a Roles ─────────────────────────────────────────────

@router.post(
    "/{role_id}/modules",
    status_code=status.HTTP_200_OK,
    summary="Vincular un módulo completo a este rol (M:N)"
)
async def assign_module_to_role(
    role_id: str,
    module_id: str,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db)
):
    """
    Vincula un módulo administrativo completo a un rol.
    Registra en la tabla pivote role_modules con auditoría.
    """
    role = await RoleService.get_by_id(db, role_id)
    if not role:
        raise HTTPException(status_code=404, detail="Rol no encontrado")

    module = await ModuleService.get_by_id(db, module_id)
    if not module:
        raise HTTPException(status_code=404, detail="Módulo no encontrado")

    creator_id = current_user["user"].id
    await RoleService.assign_module_to_role(db, role_id, module_id, creator_id=creator_id)
    return {"detail": f"Módulo '{module.nombre}' asignado al rol '{role.nombre}' correctamente"}


@router.delete(
    "/{role_id}/modules/{module_id}",
    status_code=status.HTTP_200_OK,
    summary="Desvincular un módulo de este rol"
)
async def remove_module_from_role(
    role_id: str,
    module_id: str,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db)
):
    """
    Elimina físicamente la relación entre el rol y el módulo en la tabla pivote.
    """
    role = await RoleService.get_by_id(db, role_id)
    if not role:
        raise HTTPException(status_code=404, detail="Rol no encontrado")

    module = await ModuleService.get_by_id(db, module_id)
    if not module:
        raise HTTPException(status_code=404, detail="Módulo no encontrado")

    res = await RoleService.remove_module_from_role(db, role_id, module_id)
    if not res:
        raise HTTPException(status_code=400, detail="El módulo no estaba asignado a este rol")

    return {"detail": f"Módulo '{module.nombre}' desvinculado del rol '{role.nombre}' correctamente"}


# ── Asignación de Menús a Roles ───────────────────────────────────────────────

@router.post(
    "/{role_id}/menus",
    status_code=status.HTTP_200_OK,
    summary="Asignar un ítem/submenú específico a este rol (M:N)"
)
async def assign_menu_to_role(
    role_id: str,
    menu_id: str,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db)
):
    """
    Asigna un ítem o submenú a un rol.
    Registra en la tabla pivote role_menus con auditoría.
    """
    role = await RoleService.get_by_id(db, role_id)
    if not role:
        raise HTTPException(status_code=404, detail="Rol no encontrado")

    menu = await MenuService.get_by_id(db, menu_id)
    if not menu:
        raise HTTPException(status_code=404, detail="Menú no encontrado")

    creator_id = current_user["user"].id
    await RoleService.assign_menu_to_role(db, role_id, menu_id, creator_id=creator_id)
    return {"detail": f"Menú '{menu.texto}' asignado al rol '{role.nombre}' correctamente"}


@router.delete(
    "/{role_id}/menus/{menu_id}",
    status_code=status.HTTP_200_OK,
    summary="Desasignar un ítem/submenú de este rol"
)
async def remove_menu_from_role(
    role_id: str,
    menu_id: str,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db)
):
    """
    Elimina físicamente la relación entre el rol y el menú en la tabla pivote.
    """
    role = await RoleService.get_by_id(db, role_id)
    if not role:
        raise HTTPException(status_code=404, detail="Rol no encontrado")

    menu = await MenuService.get_by_id(db, menu_id)
    if not menu:
        raise HTTPException(status_code=404, detail="Menú no encontrado")

    res = await RoleService.remove_menu_from_role(db, role_id, menu_id)
    if not res:
        raise HTTPException(status_code=400, detail="El menú no estaba asignado a este rol")

    return {"detail": f"Menú '{menu.texto}' desasignado del rol '{role.nombre}' correctamente"}
