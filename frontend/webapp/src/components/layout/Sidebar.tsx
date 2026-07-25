'use client';

import React, { useEffect, useState, useCallback } from 'react';
import Link from 'next/link';
import { usePathname, useRouter } from 'next/navigation';
import { useAuth } from '@/context/AuthContext';
import { MenusService } from '@/services/menus.service';
import {
  Shield,
  Users,
  Layers,
  Menu as MenuIcon,
  LogOut,
  LayoutDashboard,
  ChevronDown,
  ChevronRight,
  ExternalLink,
  Loader2,
  Activity,
  Server,
  Box,
  Settings,
  User,
  FileText,
  Database,
  CreditCard,
  Briefcase,
  Calendar,
  Folder,
  Home,
  ShoppingCart,
  Package,
  BarChart2,
  UserCheck,
  Bell,
} from 'lucide-react';

const ICON_MAP: Record<string, React.ElementType> = {
  Shield, Users, Layers, Menu: MenuIcon, LogOut, LayoutDashboard,
  Activity, Server, Box, Settings, User, FileText, Database, CreditCard,
  Briefcase, Calendar, Folder, Home, ShoppingCart, Package, BarChart2,
  UserCheck, Bell,
};

const renderIcon = (iconName: string | null | undefined, size = 18) => {
  if (!iconName) return null;
  const IconCmp = ICON_MAP[iconName] || MenuIcon;
  return <IconCmp size={size} />;
};

// ── Tipos ──────────────────────────────────────────────────────────────────────

interface MenuNode {
  id: string;
  texto: string;
  url?: string | null;
  icono?: string | null;
  orden?: string | null;
  parent_id?: string | null;
  modulo_id?: string | null;
  children: MenuNode[];
}

// ── Ítems de administración del Gateway (siempre visibles para admin) ─────────

const ADMIN_ITEMS = [
  { name: 'Dashboard', href: '/dashboard', icon: LayoutDashboard },
  { name: 'Roles & Permisos', href: '/dashboard/roles', icon: Shield },
  { name: 'Usuarios', href: '/dashboard/users', icon: Users },
  { name: 'Módulos', href: '/dashboard/modules', icon: Layers },
  { name: 'Menús', href: '/dashboard/menus', icon: MenuIcon },
];

// ── Componente recursivo de nodo de menú dinámico ────────────────────────────

function DynamicMenuNode({ node, depth = 0 }: { node: MenuNode; depth?: number }) {
  const pathname = usePathname();
  const hasChildren = node.children && node.children.length > 0;
  const [open, setOpen] = useState(false);

  // Auto-abrir si algún hijo está activo
  useEffect(() => {
    if (hasChildren) {
      const anyChildActive = node.children.some(
        (c) => c.url && pathname.startsWith(c.url)
      );
      if (anyChildActive) setOpen(true);
    }
  }, [pathname, hasChildren, node.children]);

  const isActive = node.url ? pathname === node.url || pathname.startsWith(node.url + '/') : false;
  const paddingLeft = `${1 + depth * 0.75}rem`;

  if (node.url && !hasChildren) {
    const isInternal = node.url.startsWith('/') || node.url.startsWith('#');
    const baseClasses = `flex items-center gap-3 py-2.5 pr-3 rounded-lg text-body-sm transition-all border-l-4 ${
      isActive
        ? 'bg-[var(--color-primary-container)] text-[var(--color-on-primary-container)] font-semibold border-[var(--color-primary)]'
        : 'text-[var(--color-on-surface)] hover:bg-[var(--color-surface-container-low)] border-transparent'
    }`;

    if (isInternal) {
      return (
        <Link href={node.url} className={baseClasses} style={{ paddingLeft }}>
          {node.icono ? renderIcon(node.icono, 18) : <ExternalLink size={18} className="opacity-50" />}
          <span className="truncate">{node.texto}</span>
        </Link>
      );
    } else {
      return (
        <a href={node.url} className={baseClasses} style={{ paddingLeft }}>
          {node.icono ? renderIcon(node.icono, 18) : <ExternalLink size={18} className="opacity-50" />}
          <span className="truncate">{node.texto}</span>
        </a>
      );
    }
  }

  return (
    <div>
      <button
        onClick={() => setOpen((v) => !v)}
        className={`w-full flex items-center gap-3 py-2.5 pr-3 rounded-lg text-body-sm transition-all border-l-4 ${
          open
            ? 'text-[var(--color-on-surface)] bg-[var(--color-surface-container-low)] border-transparent font-medium'
            : 'text-[var(--color-on-surface)] hover:bg-[var(--color-surface-container-low)] border-transparent'
        }`}
        style={{ paddingLeft }}
      >
        {node.icono ? renderIcon(node.icono, 18) : <Folder size={18} className="opacity-50" />}
        <span className="truncate flex-1 text-left">{node.texto}</span>
        {open ? <ChevronDown size={14} className="opacity-70" /> : <ChevronRight size={14} className="opacity-70" />}
      </button>

      {open && (
        <div className="mt-1 space-y-0.5">
          {node.children.map((child) => (
            <DynamicMenuNode key={child.id} node={child} depth={depth + 1} />
          ))}
        </div>
      )}
    </div>
  );
}

// ── Sidebar principal ─────────────────────────────────────────────────────────

export function Sidebar() {
  const pathname = usePathname();
  const { logout, roles, currentRole } = useAuth();

  const [dynamicMenus, setDynamicMenus] = useState<MenuNode[]>([]);
  const [menuLoading, setMenuLoading] = useState(true);
  const [menuError, setMenuError] = useState(false);
  const [userMenuOpen, setUserMenuOpen] = useState(false);

  const currentRoleName = roles.find((r) => r.id === currentRole)?.nombre || '';
  const isAdmin = currentRoleName.toLowerCase() === 'admin' || currentRoleName.toLowerCase() === 'administrador';

  // Extraer moduleId de la URL si estamos en /dashboard/module/[id]
  const activeModuleIdMatch = pathname.match(/^\/dashboard\/module\/([^/]+)/);
  const activeModuleId = activeModuleIdMatch ? activeModuleIdMatch[1] : null;
  const isInsideModule = !!activeModuleId;

  // Filtrar menús por módulo activo
  const displayedMenus = React.useMemo(() => {
    if (!activeModuleId) return [];
    return dynamicMenus.filter(node => node.modulo_id === activeModuleId);
  }, [dynamicMenus, activeModuleId]);

  const loadMenuTree = useCallback(async () => {
    setMenuLoading(true);
    setMenuError(false);
    try {
      const tree = await MenusService.getMenuTree();
      setDynamicMenus(tree);
    } catch {
      setMenuError(true);
    } finally {
      setMenuLoading(false);
    }
  }, []);

  useEffect(() => {
    loadMenuTree();
  }, [loadMenuTree, currentRole]);

  return (
    <div className="w-[var(--spacing-sidebar-width)] h-full bg-white border-r border-[var(--color-outline-variant)] flex flex-col">
      {/* ── Header ── */}
      <div className="p-5 border-b border-[var(--color-outline-variant)]">
        <Link href="/dashboard" className="flex items-center gap-2 group">
          <Shield size={22} className="text-[var(--color-primary)] group-hover:scale-110 transition-transform" />
          <h2 className="text-headline-sm text-[var(--color-primary)] font-bold">Gateway</h2>
        </Link>
        <div className="mt-2 text-body-sm text-[var(--color-on-surface-variant)] flex items-center gap-2">
          <span className="w-2 h-2 rounded-full bg-green-400 animate-pulse" />
          <span className="truncate">Rol: <strong>{currentRoleName}</strong></span>
        </div>
      </div>

      <nav className="flex-1 overflow-y-auto">
        {isAdmin ? (
          /* ── Admin: menú de administración fijo ── */
          <div className="px-3 pt-4 pb-4">
            <p className="text-[10px] font-semibold text-[var(--color-on-surface-variant)] uppercase tracking-widest mb-2 px-2">
              Administración
            </p>
            <div className="space-y-0.5">
              {ADMIN_ITEMS.map((item) => {
                const isActive =
                  pathname === item.href ||
                  (pathname.startsWith(item.href) && item.href !== '/dashboard');
                return (
                  <Link
                    key={item.href}
                    href={item.href}
                    className={`flex items-center gap-3 px-3 py-2.5 rounded-lg text-body-sm transition-all border-l-4 ${
                      isActive
                        ? 'bg-[var(--color-primary-container)] text-[var(--color-on-primary-container)] font-semibold border-[var(--color-primary)]'
                        : 'text-[var(--color-on-surface)] hover:bg-[var(--color-surface-container-low)] border-transparent'
                    }`}
                  >
                    <item.icon size={18} />
                    {item.name}
                  </Link>
                );
              })}
            </div>
          </div>
        ) : isInsideModule ? (
          /* ── No-Admin dentro de un módulo: menú del módulo ── */
          <div className="px-3 pt-4 pb-4">
            <Link
              href="/dashboard"
              className="flex items-center gap-2 px-3 py-2 mb-3 text-body-sm text-[var(--color-on-surface-variant)] hover:text-[var(--color-primary)] hover:bg-[var(--color-surface-container-low)] rounded-lg transition-all"
            >
              <Home size={16} />
              <span>Inicio (Módulos)</span>
            </Link>

            <div className="mx-2 mb-3 border-t border-[var(--color-outline-variant)]" />

            <p className="text-[10px] font-semibold text-[var(--color-on-surface-variant)] uppercase tracking-widest mb-2 px-2">
              Menú del Módulo
            </p>

            {menuLoading ? (
              <div className="space-y-2 px-1 mt-2">
                {[1, 2, 3].map((i) => (
                  <div key={i} className="h-8 bg-[var(--color-surface-container-low)] rounded-lg animate-pulse" />
                ))}
              </div>
            ) : menuError ? (
              <div className="px-2 py-2 text-body-sm text-[var(--color-on-surface-variant)] italic">
                Error al cargar menús.{' '}
                <button onClick={loadMenuTree} className="underline text-[var(--color-primary)]">
                  Reintentar
                </button>
              </div>
            ) : displayedMenus.length === 0 ? (
              <div className="px-2 py-3 text-body-sm text-[var(--color-on-surface-variant)] italic">
                Este módulo no tiene menús asignados.
              </div>
            ) : (
              <div className="space-y-0.5">
                {displayedMenus.map((node) => (
                  <DynamicMenuNode key={node.id} node={node} depth={0} />
                ))}
              </div>
            )}
          </div>
        ) : (
          /* ── No-Admin en home: sin menú lateral ── */
          <div className="px-3 pt-6 pb-4 flex flex-col items-center text-center">
            <div className="w-16 h-16 bg-[var(--color-primary-container)] text-[var(--color-on-primary-container)] rounded-full flex items-center justify-center mb-3">
              <Layers size={28} />
            </div>
            <p className="text-body-sm text-[var(--color-on-surface-variant)]">
              Selecciona un módulo para ver sus opciones.
            </p>
          </div>
        )}
      </nav>

      {/* ── Footer: Usuario + Logout ── */}
      <div className="p-3 border-t border-[var(--color-outline-variant)]">
        <div className="relative">
          <button
            onClick={() => setUserMenuOpen(v => !v)}
            className="flex items-center gap-3 w-full px-3 py-2.5 rounded-lg text-body-sm text-[var(--color-on-surface)] hover:bg-[var(--color-surface-container-low)] transition-all"
          >
            <div className="w-8 h-8 bg-[var(--color-primary)] text-white rounded-full flex items-center justify-center font-bold text-sm flex-shrink-0">
              {currentRoleName.charAt(0).toUpperCase()}
            </div>
            <div className="flex-1 text-left overflow-hidden">
              <p className="truncate text-body-sm font-medium">{currentRoleName}</p>
              <p className="text-[11px] text-[var(--color-on-surface-variant)] truncate">Sesión activa</p>
            </div>
            <ChevronDown size={14} className={`opacity-60 transition-transform ${userMenuOpen ? 'rotate-180' : ''}`} />
          </button>

          {userMenuOpen && (
            <div className="absolute bottom-full left-0 right-0 mb-1 bg-white rounded-lg shadow-elevation-3 border border-[var(--color-outline-variant)] overflow-hidden">
              <button
                onClick={logout}
                className="flex items-center gap-3 w-full px-4 py-3 text-body-sm text-[var(--color-error)] hover:bg-[var(--color-error-container)] transition-colors"
              >
                <LogOut size={16} />
                Cerrar Sesión
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
