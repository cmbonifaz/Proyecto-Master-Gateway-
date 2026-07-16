'use client';

import React, { useEffect, useState, useCallback } from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
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
} from 'lucide-react';

// ── Tipos ──────────────────────────────────────────────────────────────────────

interface MenuNode {
  id: string;
  texto: string;
  url?: string | null;
  icono?: string | null;
  orden?: string | null;
  parent_id?: string | null;
  children: MenuNode[];
}

// ── Ítems de administración del Gateway (siempre visibles) ───────────────────

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

  // Nodo con URL — enlace de navegación
  if (node.url && !hasChildren) {
    return (
      <Link
        href={node.url}
        className={`flex items-center gap-2 py-2 pr-3 rounded text-body-sm transition-all border-l-2 ${
          isActive
            ? 'bg-[var(--color-secondary-container)] text-[var(--color-on-secondary-container)] font-semibold border-[var(--color-secondary)]'
            : 'text-[var(--color-on-surface)] hover:bg-[var(--color-surface-container-low)] border-transparent'
        }`}
        style={{ paddingLeft }}
      >
        {node.icono ? (
          <span className="text-xs opacity-70 flex-shrink-0">{node.icono}</span>
        ) : (
          <ExternalLink size={13} className="flex-shrink-0 opacity-50" />
        )}
        <span className="truncate">{node.texto}</span>
      </Link>
    );
  }

  // Nodo contenedor (sin URL, tiene hijos) — colapsable
  return (
    <div>
      <button
        onClick={() => setOpen((v) => !v)}
        className={`w-full flex items-center gap-2 py-2 pr-3 rounded text-body-sm transition-all border-l-2 ${
          open
            ? 'text-[var(--color-on-surface)] bg-[var(--color-surface-container-low)] border-[var(--color-outline-variant)]'
            : 'text-[var(--color-on-surface-variant)] hover:bg-[var(--color-surface-container-low)] border-transparent'
        }`}
        style={{ paddingLeft }}
      >
        {node.icono ? (
          <span className="text-xs opacity-70 flex-shrink-0">{node.icono}</span>
        ) : (
          <MenuIcon size={13} className="flex-shrink-0 opacity-50" />
        )}
        <span className="truncate flex-1 text-left">{node.texto}</span>
        {open ? <ChevronDown size={13} /> : <ChevronRight size={13} />}
      </button>

      {open && (
        <div className="mt-0.5 space-y-0.5">
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

  const currentRoleName = roles.find((r) => r.id === currentRole)?.nombre || 'Admin';

  // Cargar árbol de menús dinámico según el rol del token
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
  }, [loadMenuTree, currentRole]); // Recargar si cambia el rol activo

  return (
    <div className="w-[var(--spacing-sidebar-width)] h-full bg-white border-r border-[var(--color-outline-variant)] flex flex-col">
      {/* ── Header ── */}
      <div className="p-6 border-b border-[var(--color-outline-variant)]">
        <h2 className="text-headline-sm text-[var(--color-primary)] font-bold flex items-center gap-2">
          <Shield size={24} />
          Gateway
        </h2>
        <div className="mt-2 text-body-sm text-[var(--color-on-surface-variant)] flex items-center gap-2">
          <span className="w-2 h-2 rounded-full bg-green-400 animate-pulse" />
          <span className="truncate">Rol activo: <strong>{currentRoleName}</strong></span>
        </div>
      </div>

      <nav className="flex-1 overflow-y-auto">
        {/* ── Sección Administración del Gateway (hardcoded, siempre visible) ── */}
        <div className="px-4 pt-4 pb-2">
          <p className="text-label-md text-[var(--color-on-surface-variant)] uppercase tracking-wider mb-2 px-1 text-xs">
            Administración
          </p>
          <div className="space-y-1">
            {ADMIN_ITEMS.map((item) => {
              const isActive =
                pathname === item.href ||
                (pathname.startsWith(item.href) && item.href !== '/dashboard');
              return (
                <Link
                  key={item.href}
                  href={item.href}
                  className={`flex items-center gap-3 px-3 py-2.5 rounded text-body-sm transition-colors border-l-4 ${
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

        {/* ── Divisor ── */}
        <div className="mx-4 my-3 border-t border-[var(--color-outline-variant)]" />

        {/* ── Sección Menús Dinámicos (por rol, desde la API) ── */}
        <div className="px-4 pb-4">
          <div className="flex items-center justify-between mb-2 px-1">
            <p className="text-label-md text-[var(--color-on-surface-variant)] uppercase tracking-wider text-xs">
              Acceso por Rol
            </p>
            {menuLoading && <Loader2 size={12} className="animate-spin text-[var(--color-on-surface-variant)]" />}
          </div>

          {menuLoading ? (
            <div className="space-y-2 px-1">
              {[1, 2, 3].map((i) => (
                <div key={i} className="h-8 bg-[var(--color-surface-container-low)] rounded animate-pulse" />
              ))}
            </div>
          ) : menuError ? (
            <div className="px-1 py-2 text-body-sm text-[var(--color-on-surface-variant)] italic">
              No se pudieron cargar los menús.{' '}
              <button onClick={loadMenuTree} className="underline text-[var(--color-primary)]">
                Reintentar
              </button>
            </div>
          ) : dynamicMenus.length === 0 ? (
            <div className="px-1 py-2 text-body-sm text-[var(--color-on-surface-variant)] italic">
              Sin menús asignados para este rol.
            </div>
          ) : (
            <div className="space-y-0.5">
              {dynamicMenus.map((node) => (
                <DynamicMenuNode key={node.id} node={node} depth={0} />
              ))}
            </div>
          )}
        </div>
      </nav>

      {/* ── Footer — Cerrar Sesión ── */}
      <div className="p-4 border-t border-[var(--color-outline-variant)]">
        <button
          onClick={logout}
          className="flex items-center gap-3 w-full px-3 py-2.5 text-body-sm text-[var(--color-error)] hover:bg-[var(--color-error-container)] rounded transition-colors"
        >
          <LogOut size={18} />
          Cerrar Sesión
        </button>
      </div>
    </div>
  );
}
