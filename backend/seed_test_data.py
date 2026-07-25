# -*- coding: utf-8 -*-
"""
seed_test_data.py — Datos de prueba completos para el Master Gateway.
Crea múltiples roles con sus módulos y menús correctamente vinculados.
"""
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
        print("\n========================================")
        print("  SEED DE DATOS DE PRUEBA — Gateway")
        print("========================================\n")

        # ─────────────────────────────────────────────────────────────────────
        # 1. MÓDULOS
        # ─────────────────────────────────────────────────────────────────────
        print("[*] Creando módulos...")

        async def get_or_create_module(nombre, descripcion):
            result = await db.execute(select(Module).filter_by(nombre=nombre))
            mod = result.scalars().first()
            if not mod:
                mod = Module(nombre=nombre, descripcion=descripcion, estado="ACTIVO")
                db.add(mod)
                await db.flush()
                print(f"  [+] Módulo creado: {nombre}")
            else:
                print(f"  [=] Módulo ya existe: {nombre}")
            return mod

        mod_ventas    = await get_or_create_module("Gestión de Ventas",     "Pedidos, clientes, cotizaciones y facturación")
        mod_inventario= await get_or_create_module("Inventario",            "Control de productos, stock y bodegas")
        mod_rrhh      = await get_or_create_module("Recursos Humanos",      "Empleados, nómina, vacaciones y contratos")
        mod_reportes  = await get_or_create_module("Reportes & Analytics",  "Dashboards, KPIs y exportación de datos")
        mod_seguridad = await get_or_create_module("Seguridad",             "Roles, usuarios, permisos y auditoría")

        # ─────────────────────────────────────────────────────────────────────
        # 2. ROLES
        # ─────────────────────────────────────────────────────────────────────
        print("\n[*] Creando roles...")

        async def get_or_create_role(nombre, descripcion):
            result = await db.execute(select(Role).filter_by(nombre=nombre))
            role = result.scalars().first()
            if not role:
                role = Role(nombre=nombre, descripcion=descripcion, estado="ACTIVO")
                db.add(role)
                await db.flush()
                print(f"  [+] Rol creado: {nombre}")
            else:
                print(f"  [=] Rol ya existe: {nombre}")
            return role

        role_admin    = await get_or_create_role("ADMIN",      "Administrador completo del sistema")
        role_vendedor = await get_or_create_role("VENDEDOR",   "Acceso a ventas, clientes y reportes")
        role_bodega   = await get_or_create_role("BODEGUERO",  "Acceso a inventario y reportes básicos")
        role_rrhh     = await get_or_create_role("RRHH",       "Acceso a recursos humanos y reportes")

        # ─────────────────────────────────────────────────────────────────────
        # 3. USUARIOS DE PRUEBA
        # ─────────────────────────────────────────────────────────────────────
        print("\n[*] Creando usuarios de prueba...")

        async def get_or_create_user(email, password, nombre):
            result = await db.execute(select(User).filter_by(email=email))
            user = result.scalars().first()
            if not user:
                user = User(
                    email=email,
                    password_hash=hash_password(password),
                    nombre=nombre,
                    estado="ACTIVO"
                )
                db.add(user)
                await db.flush()
                print(f"  [+] Usuario creado: {email} / {password}")
            else:
                print(f"  [=] Usuario ya existe: {email}")
            return user

        user_admin    = await get_or_create_user("admin@gateway.com",    "AdminPass123!",    "Administrador Sistema")
        user_vendedor = await get_or_create_user("vendedor@gateway.com", "Vendedor123!",     "Carlos Pérez (Vendedor)")
        user_bodega   = await get_or_create_user("bodega@gateway.com",   "Bodega123!",       "María García (Bodega)")
        user_rrhh     = await get_or_create_user("rrhh@gateway.com",     "RRHH123!",         "Juan Rodríguez (RRHH)")

        # ─────────────────────────────────────────────────────────────────────
        # 4. ASIGNAR ROLES A USUARIOS
        # ─────────────────────────────────────────────────────────────────────
        print("\n[*] Asignando roles a usuarios...")

        async def assign_role(user, role):
            result = await db.execute(select(UserRole).filter_by(user_id=user.id, role_id=role.id))
            link = result.scalars().first()
            if not link:
                link = UserRole(user_id=user.id, role_id=role.id, estado="ACTIVO")
                db.add(link)
                print(f"  [+] {user.email} -> {role.nombre}")
            return link

        await assign_role(user_admin,    role_admin)
        await assign_role(user_vendedor, role_vendedor)
        await assign_role(user_bodega,   role_bodega)
        await assign_role(user_rrhh,     role_rrhh)

        # ─────────────────────────────────────────────────────────────────────
        # 5. ASIGNAR MÓDULOS A ROLES
        # ─────────────────────────────────────────────────────────────────────
        print("\n[*] Asignando módulos a roles...")

        async def assign_module(role, module):
            result = await db.execute(select(RoleModule).filter_by(role_id=role.id, module_id=module.id))
            link = result.scalars().first()
            if not link:
                link = RoleModule(role_id=role.id, module_id=module.id)
                db.add(link)
                print(f"  [+] Modulo '{module.nombre}' -> Rol '{role.nombre}'")
            return link

        # ADMIN: acceso a todo
        await assign_module(role_admin, mod_ventas)
        await assign_module(role_admin, mod_inventario)
        await assign_module(role_admin, mod_rrhh)
        await assign_module(role_admin, mod_reportes)
        await assign_module(role_admin, mod_seguridad)
        # VENDEDOR: ventas y reportes
        await assign_module(role_vendedor, mod_ventas)
        await assign_module(role_vendedor, mod_reportes)
        # BODEGUERO: inventario y reportes
        await assign_module(role_bodega, mod_inventario)
        await assign_module(role_bodega, mod_reportes)
        # RRHH: rrhh y reportes
        await assign_module(role_rrhh, mod_rrhh)
        await assign_module(role_rrhh, mod_reportes)

        # ─────────────────────────────────────────────────────────────────────
        # 6. CREAR MENÚS CON modulo_id CORRECTO
        # ─────────────────────────────────────────────────────────────────────
        print("\n[*] Creando menús...")

        async def get_or_create_menu(texto, modulo, orden, url=None, icono=None, parent=None):
            result = await db.execute(select(Menu).filter_by(texto=texto, modulo_id=modulo.id))
            menu = result.scalars().first()
            if not menu:
                menu = Menu(
                    texto=texto,
                    url=url,
                    icono=icono,
                    orden=orden,
                    parent_id=parent.id if parent else None,
                    modulo_id=modulo.id,
                    estado="ACTIVO"
                )
                db.add(menu)
                await db.flush()
                print(f"  [+] Menú: {texto} ({modulo.nombre})")
            else:
                print(f"  [=] Menú ya existe: {texto}")
            return menu

        # ── Menús de Gestión de Ventas ──
        m_ventas_root     = await get_or_create_menu("Ventas",          mod_ventas,    "001", icono="ShoppingCart")
        m_clientes        = await get_or_create_menu("Clientes",        mod_ventas,    "002", url="/dashboard/ventas/clientes",    icono="Users",       parent=m_ventas_root)
        m_pedidos         = await get_or_create_menu("Pedidos",         mod_ventas,    "003", url="/dashboard/ventas/pedidos",     icono="Package",     parent=m_ventas_root)
        m_cotizaciones    = await get_or_create_menu("Cotizaciones",    mod_ventas,    "004", url="/dashboard/ventas/cotizaciones",icono="FileText",    parent=m_ventas_root)
        m_facturas        = await get_or_create_menu("Facturación",     mod_ventas,    "005", url="/dashboard/ventas/facturas",    icono="CreditCard",  parent=m_ventas_root)

        # ── Menús de Inventario ──
        m_inv_root        = await get_or_create_menu("Inventario",       mod_inventario,"001", icono="Database")
        m_productos       = await get_or_create_menu("Productos",        mod_inventario,"002", url="/dashboard/inventario/productos",icono="Box",       parent=m_inv_root)
        m_bodegas         = await get_or_create_menu("Bodegas",          mod_inventario,"003", url="/dashboard/inventario/bodegas",  icono="Briefcase", parent=m_inv_root)
        m_entradas        = await get_or_create_menu("Entradas",         mod_inventario,"004", url="/dashboard/inventario/entradas", icono="Activity",  parent=m_inv_root)
        m_salidas         = await get_or_create_menu("Salidas",          mod_inventario,"005", url="/dashboard/inventario/salidas",  icono="Activity",  parent=m_inv_root)

        # ── Menús de RRHH ──
        m_rrhh_root       = await get_or_create_menu("RRHH",             mod_rrhh,      "001", icono="UserCheck")
        m_empleados       = await get_or_create_menu("Empleados",        mod_rrhh,      "002", url="/dashboard/rrhh/empleados",   icono="Users",       parent=m_rrhh_root)
        m_nomina          = await get_or_create_menu("Nómina",           mod_rrhh,      "003", url="/dashboard/rrhh/nomina",      icono="CreditCard",  parent=m_rrhh_root)
        m_vacaciones      = await get_or_create_menu("Vacaciones",       mod_rrhh,      "004", url="/dashboard/rrhh/vacaciones",  icono="Calendar",    parent=m_rrhh_root)
        m_contratos       = await get_or_create_menu("Contratos",        mod_rrhh,      "005", url="/dashboard/rrhh/contratos",   icono="FileText",    parent=m_rrhh_root)

        # ── Menús de Reportes ──
        m_rep_root        = await get_or_create_menu("Reportes",         mod_reportes,  "001", icono="BarChart2")
        m_kpis            = await get_or_create_menu("KPIs & Métricas",  mod_reportes,  "002", url="/dashboard/reportes/kpis",    icono="Activity",    parent=m_rep_root)
        m_exportar        = await get_or_create_menu("Exportar Datos",   mod_reportes,  "003", url="/dashboard/reportes/export",  icono="FileText",    parent=m_rep_root)

        # ── Menús de Seguridad (para admin) ──
        m_seg_root        = await get_or_create_menu("Seguridad",        mod_seguridad, "001", icono="Shield")
        m_seg_usuarios    = await get_or_create_menu("Usuarios",         mod_seguridad, "002", url="/dashboard/users",    icono="Users",       parent=m_seg_root)
        m_seg_roles       = await get_or_create_menu("Roles",            mod_seguridad, "003", url="/dashboard/roles",    icono="Shield",      parent=m_seg_root)
        m_seg_modulos     = await get_or_create_menu("Módulos",          mod_seguridad, "004", url="/dashboard/modules",  icono="Layers",      parent=m_seg_root)
        m_seg_menus       = await get_or_create_menu("Menús",            mod_seguridad, "005", url="/dashboard/menus",    icono="Menu",        parent=m_seg_root)

        # ─────────────────────────────────────────────────────────────────────
        # 7. ASIGNAR MENÚS A ROLES
        # ─────────────────────────────────────────────────────────────────────
        print("\n[*] Asignando menús a roles...")

        async def assign_menu(role, menu):
            result = await db.execute(select(RoleMenu).filter_by(role_id=role.id, menu_id=menu.id))
            link = result.scalars().first()
            if not link:
                link = RoleMenu(role_id=role.id, menu_id=menu.id)
                db.add(link)

        # VENDEDOR → Menús de Ventas
        for m in [m_ventas_root, m_clientes, m_pedidos, m_cotizaciones, m_facturas]:
            await assign_menu(role_vendedor, m)
        # VENDEDOR → Menús de Reportes
        for m in [m_rep_root, m_kpis, m_exportar]:
            await assign_menu(role_vendedor, m)
        print("  [+] Menús asignados a VENDEDOR")

        # BODEGUERO → Menús de Inventario
        for m in [m_inv_root, m_productos, m_bodegas, m_entradas, m_salidas]:
            await assign_menu(role_bodega, m)
        # BODEGUERO → Menús de Reportes
        for m in [m_rep_root, m_kpis]:
            await assign_menu(role_bodega, m)
        print("  [+] Menús asignados a BODEGUERO")

        # RRHH → Menús de RRHH
        for m in [m_rrhh_root, m_empleados, m_nomina, m_vacaciones, m_contratos]:
            await assign_menu(role_rrhh, m)
        # RRHH → Menús de Reportes
        for m in [m_rep_root, m_kpis, m_exportar]:
            await assign_menu(role_rrhh, m)
        print("  [+] Menús asignados a RRHH")

        # ADMIN → Todos los menús
        todos = [
            m_ventas_root, m_clientes, m_pedidos, m_cotizaciones, m_facturas,
            m_inv_root, m_productos, m_bodegas, m_entradas, m_salidas,
            m_rrhh_root, m_empleados, m_nomina, m_vacaciones, m_contratos,
            m_rep_root, m_kpis, m_exportar,
            m_seg_root, m_seg_usuarios, m_seg_roles, m_seg_modulos, m_seg_menus,
        ]
        for m in todos:
            await assign_menu(role_admin, m)
        print("  [+] Menús asignados a ADMIN")

        await db.commit()
        print("\n========================================")
        print("  ✅ Seed completado exitosamente!")
        print("========================================")
        print("\nCuentas creadas:")
        print("  admin@gateway.com     / AdminPass123!   (ADMIN)")
        print("  vendedor@gateway.com  / Vendedor123!    (VENDEDOR)")
        print("  bodega@gateway.com    / Bodega123!      (BODEGUERO)")
        print("  rrhh@gateway.com      / RRHH123!        (RRHH)")
        print()


if __name__ == "__main__":
    asyncio.run(seed())
