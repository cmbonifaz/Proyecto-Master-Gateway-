# -*- coding: utf-8 -*-
"""
menu_service.py — Servicio para gestionar la jerarquía de menús (recursivos con CTE).
"""
from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from sqlalchemy.orm import aliased
from app.models.menu import Menu
from app.models.role_menu import RoleMenu
from app.schemas.menu import MenuCreate, MenuUpdate, MenuNode


class MenuService:
    @staticmethod
    async def get_by_id(db: AsyncSession, menu_id: str) -> Optional[Menu]:
        stmt = select(Menu).where(Menu.id == menu_id, Menu.estado == "ACTIVO")
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    @staticmethod
    async def list_active(db: AsyncSession, skip: int = 0, limit: int = 100) -> List[Menu]:
        stmt = select(Menu).where(Menu.estado == "ACTIVO").offset(skip).limit(limit)
        result = await db.execute(stmt)
        return list(result.scalars().all())

    @staticmethod
    async def create(db: AsyncSession, obj_in: MenuCreate, creator_id: Optional[str] = None) -> Menu:
        db_obj = Menu(
            texto=obj_in.texto,
            url=obj_in.url,
            icono=obj_in.icono,
            orden=obj_in.orden,
            parent_id=obj_in.parent_id,
            modulo_id=obj_in.modulo_id,
            creado_por=creator_id,
            actualizado_por=creator_id
        )
        db.add(db_obj)
        await db.flush()
        await db.refresh(db_obj)
        return db_obj

    @staticmethod
    async def update(db: AsyncSession, db_obj: Menu, obj_in: MenuUpdate, updater_id: Optional[str] = None) -> Menu:
        if obj_in.texto is not None:
            db_obj.texto = obj_in.texto
        if obj_in.url is not None:
            db_obj.url = obj_in.url
        if obj_in.icono is not None:
            db_obj.icono = obj_in.icono
        if obj_in.orden is not None:
            db_obj.orden = obj_in.orden
        if obj_in.parent_id is not None:
            # Prevenir auto-referencia cíclica básica
            if obj_in.parent_id == db_obj.id:
                raise ValueError("Un menú no puede ser su propio padre.")
            db_obj.parent_id = obj_in.parent_id
            
        if obj_in.modulo_id is not None:
            db_obj.modulo_id = obj_in.modulo_id
            
        db_obj.actualizado_por = updater_id
        db.add(db_obj)
        await db.flush()
        await db.refresh(db_obj)
        return db_obj

    @staticmethod
    async def delete(db: AsyncSession, db_obj: Menu, updater_id: Optional[str] = None) -> Menu:
        db_obj.soft_delete(updated_by=updater_id)
        db.add(db_obj)
        await db.flush()
        return db_obj

    # ── Árbol Jerárquico Recursivo (CTE) ───────────────────────────────────────
    @staticmethod
    async def get_menu_tree_for_role(db: AsyncSession, role_id: str) -> List[MenuNode]:
        """
        Obtiene el árbol de menús completo asignado a un rol específico.
        Usa una query recursiva (CTE) para evitar el problema N+1 y 
        garantizar la integridad de los nodos ancestros.
        """
        # Expresión Común de Tabla (CTE) recursiva
        # Anchor: Menús asignados directamente al rol
        anchor = (
            select(
                Menu.id,
                Menu.texto,
                Menu.url,
                Menu.icono,
                Menu.orden,
                Menu.parent_id,
                Menu.modulo_id,
                Menu.estado
            )
            .join(RoleMenu, Menu.id == RoleMenu.menu_id)
            .where(and_(RoleMenu.role_id == role_id, Menu.estado == "ACTIVO"))
            .cte(name="menu_tree_cte", recursive=True)
        )

        # Miembro recursivo: Obtener los padres de esos menús para asegurar que no queden huérfanos
        menu_alias = aliased(Menu)
        recursive_part = (
            select(
                menu_alias.id,
                menu_alias.texto,
                menu_alias.url,
                menu_alias.icono,
                menu_alias.orden,
                menu_alias.parent_id,
                menu_alias.modulo_id,
                menu_alias.estado
            )
            .join(anchor, anchor.c.parent_id == menu_alias.id)
            .where(menu_alias.estado == "ACTIVO")
        )

        # Unir ambas partes
        cte_union = anchor.union_all(recursive_part)

        # Seleccionar único/distinto del árbol recursivo para remover duplicidades
        stmt = select(
            cte_union.c.id,
            cte_union.c.texto,
            cte_union.c.url,
            cte_union.c.icono,
            cte_union.c.orden,
            cte_union.c.parent_id,
            cte_union.c.modulo_id
        ).distinct()

        result = await db.execute(stmt)
        rows = result.fetchall()

        # Construir estructura de árbol en memoria (O(N))
        nodes_dict: Dict[str, Dict[str, Any]] = {}
        for row in rows:
            nodes_dict[row.id] = {
                "id": row.id,
                "texto": row.texto,
                "url": row.url,
                "icono": row.icono,
                "orden": row.orden,
                "parent_id": row.parent_id,
                "modulo_id": row.modulo_id,
                "children": []
            }

        roots: List[Dict[str, Any]] = []
        for node in nodes_dict.values():
            p_id = node["parent_id"]
            if p_id and p_id in nodes_dict:
                nodes_dict[p_id]["children"].append(node)
            else:
                roots.append(node)

        # Ordenar cada nivel según el campo 'orden'
        def sort_node(n: Dict[str, Any]):
            n["children"].sort(key=lambda x: x["orden"] or "")
            for child in n["children"]:
                sort_node(child)

        roots.sort(key=lambda x: x["orden"] or "")
        for r in roots:
            sort_node(r)

        return [MenuNode(**r) for r in roots]
