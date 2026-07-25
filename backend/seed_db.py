# -*- coding: utf-8 -*-
import asyncio
from sqlalchemy.future import select
from app.core.database import AsyncSessionLocal
from app.models.user import User
from app.models.role import Role
from app.models.user_role import UserRole
from app.models.module import Module
from app.models.menu import Menu
from app.models.role_module import RoleModule
from app.models.role_menu import RoleMenu
from app.core.security import hash_password

async def seed():
    async with AsyncSessionLocal() as db:
        print("[*] Conectando a la base de datos...")
        
        # 1. Crear Rol ADMIN si no existe
        print("[*] Verificando rol ADMIN...")
        result = await db.execute(select(Role).filter_by(nombre="ADMIN"))
        admin_role = result.scalars().first()
        if not admin_role:
            print("[+] Creando rol ADMIN...")
            admin_role = Role(
                nombre="ADMIN",
                descripcion="Administrador completo del sistema",
                estado="ACTIVO"
            )
            db.add(admin_role)
            await db.flush()
        else:
            print("[*] El rol ADMIN ya existe.")

        # 2. Crear usuario administrador si no existe
        print("[*] Verificando usuario administrador...")
        result = await db.execute(select(User).filter_by(email="admin@example.com"))
        admin_user = result.scalars().first()
        if not admin_user:
            print("[+] Creando usuario admin@example.com...")
            admin_user = User(
                email="admin@example.com",
                password_hash=hash_password("AdminPass123!"),
                nombre="Administrador Sistema",
                estado="ACTIVO"
            )
            db.add(admin_user)
            await db.flush()
        else:
            print("[*] El usuario admin@example.com ya existe.")

        # 3. Asociar usuario y rol en user_roles
        result = await db.execute(select(UserRole).filter_by(user_id=admin_user.id, role_id=admin_role.id))
        user_role_link = result.scalars().first()
        if not user_role_link:
            print("[+] Asignando rol ADMIN a admin@example.com...")
            user_role_link = UserRole(
                user_id=admin_user.id,
                role_id=admin_role.id,
                estado="ACTIVO"
            )
            db.add(user_role_link)
        else:
            print("[*] El rol ADMIN ya está asignado al administrador.")

        # 4. Crear Módulo de Seguridad si no existe
        print("[*] Verificando módulo de Seguridad...")
        result = await db.execute(select(Module).filter_by(nombre="Seguridad"))
        seg_module = result.scalars().first()
        if not seg_module:
            print("[+] Creando módulo Seguridad...")
            seg_module = Module(
                nombre="Seguridad",
                descripcion="Módulo para gestionar seguridad, roles y accesos",
                estado="ACTIVO"
            )
            db.add(seg_module)
            await db.flush()
        else:
            print("[*] El módulo Seguridad ya existe.")

        # Asociar módulo al rol ADMIN
        result = await db.execute(select(RoleModule).filter_by(role_id=admin_role.id, module_id=seg_module.id))
        role_mod_link = result.scalars().first()
        if not role_mod_link:
            print("[+] Vinculando módulo Seguridad al rol ADMIN...")
            role_mod_link = RoleModule(
                role_id=admin_role.id,
                module_id=seg_module.id
            )
            db.add(role_mod_link)

        # 5. Crear Menús de ejemplo si no existen
        print("[*] Verificando menús del Dashboard...")
        result = await db.execute(select(Menu).filter_by(texto="Dashboard"))
        dash_menu = result.scalars().first()
        if not dash_menu:
            print("[+] Creando menú raíz Dashboard...")
            dash_menu = Menu(
                texto="Dashboard",
                url=None,
                icono="LayoutDashboard",
                orden="001",
                estado="ACTIVO"
            )
            db.add(dash_menu)
            await db.flush()
        
        result = await db.execute(select(Menu).filter_by(texto="Menus"))
        menus_menu = result.scalars().first()
        if not menus_menu:
            print("[+] Creando submenú Menus...")
            menus_menu = Menu(
                texto="Menus",
                url="/dashboard/menus",
                icono="Menu",
                orden="002",
                parent_id=dash_menu.id,
                estado="ACTIVO"
            )
            db.add(menus_menu)
            await db.flush()

        # Asociar los menús al rol ADMIN
        for menu in [dash_menu, menus_menu]:
            result = await db.execute(select(RoleMenu).filter_by(role_id=admin_role.id, menu_id=menu.id))
            role_menu_link = result.scalars().first()
            if not role_menu_link:
                print(f"[+] Vinculando menú '{menu.texto}' al rol ADMIN...")
                role_menu_link = RoleMenu(
                    role_id=admin_role.id,
                    menu_id=menu.id
                )
                db.add(role_menu_link)

        await db.commit()
        print("[+] ¡Proceso de inicialización de base de datos finalizado con éxito!")

if __name__ == "__main__":
    asyncio.run(seed())
