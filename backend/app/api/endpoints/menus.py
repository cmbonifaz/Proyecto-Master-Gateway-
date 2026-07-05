# -*- coding: utf-8 -*-
"""
menus.py — Endpoints HTTP para la administración de Menús e ítems (recursivo/árbol).
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.core.database import get_db
from app.core.dependencies import get_current_user, CurrentUser
from app.schemas.menu import MenuCreate, MenuUpdate, MenuResponse, MenuNode
from app.services.menu_service import MenuService

router = APIRouter()


@router.get("/", response_model=List[MenuResponse], summary="Listar menús activos")
async def list_menus(
    skip: int = 0, 
    limit: int = 100,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db)
):
    return await MenuService.list_active(db, skip=skip, limit=limit)


@router.get("/tree", response_model=List[MenuNode], summary="Obtener árbol de menús jerárquico recursivo")
async def get_menu_tree(
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db)
):
    """
    Retorna el árbol recursivo de menús (CTE) correspondiente al ROL seleccionado 
    del usuario logueado en la sesión (Zero Trust).
    """
    role_id = current_user.get("role_id")
    if not role_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No se ha detectado rol activo en el token"
        )
    return await MenuService.get_menu_tree_for_role(db, role_id)


@router.get("/{menu_id}", response_model=MenuResponse, summary="Obtener menú por ID")
async def get_menu(
    menu_id: str,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db)
):
    menu = await MenuService.get_by_id(db, menu_id)
    if not menu:
        raise HTTPException(status_code=404, detail="Menú no encontrado")
    return menu


@router.post("/", response_model=MenuResponse, status_code=status.HTTP_201_CREATED, summary="Crear un menú")
async def create_menu(
    obj_in: MenuCreate,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db)
):
    creator_id = current_user["user"].id
    return await MenuService.create(db, obj_in, creator_id=creator_id)


@router.put("/{menu_id}", response_model=MenuResponse, summary="Actualizar un menú")
async def update_menu(
    menu_id: str,
    obj_in: MenuUpdate,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db)
):
    menu = await MenuService.get_by_id(db, menu_id)
    if not menu:
        raise HTTPException(status_code=404, detail="Menú no encontrado")
        
    updater_id = current_user["user"].id
    try:
        return await MenuService.update(db, menu, obj_in, updater_id=updater_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{menu_id}", response_model=MenuResponse, summary="Eliminar un menú (Soft Delete)")
async def delete_menu(
    menu_id: str,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db)
):
    menu = await MenuService.get_by_id(db, menu_id)
    if not menu:
        raise HTTPException(status_code=404, detail="Menú no encontrado")
        
    updater_id = current_user["user"].id
    return await MenuService.delete(db, menu, updater_id=updater_id)
