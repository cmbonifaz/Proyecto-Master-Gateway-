'use client';

import React from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { useAuth } from '@/context/AuthContext';
import { Shield, Users, Layers, Menu as MenuIcon, LogOut, LayoutDashboard } from 'lucide-react';

export function Sidebar() {
  const pathname = usePathname();
  const { logout, roles, currentRole } = useAuth();

  const navItems = [
    { name: 'Dashboard', href: '/dashboard', icon: LayoutDashboard },
    { name: 'Roles & Permisos', href: '/dashboard/roles', icon: Shield },
    { name: 'Usuarios', href: '/dashboard/users', icon: Users },
    { name: 'Módulos', href: '/dashboard/modules', icon: Layers },
    { name: 'Menús', href: '/dashboard/menus', icon: MenuIcon },
  ];

  const currentRoleName = roles.find((r) => r.id === currentRole)?.nombre || 'Admin';

  return (
    <div className="w-[var(--spacing-sidebar-width)] h-full bg-white border-r border-[var(--color-outline-variant)] flex flex-col">
      <div className="p-6 border-b border-[var(--color-outline-variant)]">
        <h2 className="text-headline-sm text-[var(--color-primary)] font-bold flex items-center gap-2">
          <Shield size={24} />
          Gateway
        </h2>
        <div className="mt-2 text-body-sm text-[var(--color-on-surface-variant)] flex items-center gap-2">
          <span className="w-2 h-2 rounded-full bg-[var(--color-tertiary-container)]"></span>
          Rol activo: {currentRoleName}
        </div>
      </div>

      <nav className="flex-1 p-4 space-y-2 overflow-y-auto">
        {navItems.map((item) => {
          const isActive = pathname === item.href || (pathname.startsWith(item.href) && item.href !== '/dashboard');
          return (
            <Link
              key={item.href}
              href={item.href}
              className={`flex items-center gap-3 px-4 py-3 rounded text-body-md transition-colors ${
                isActive
                  ? 'bg-[var(--color-primary-container)] text-[var(--color-on-primary-container)] font-semibold border-l-4 border-[var(--color-primary)]'
                  : 'text-[var(--color-on-surface)] hover:bg-[var(--color-surface-container-low)] border-l-4 border-transparent'
              }`}
            >
              <item.icon size={20} />
              {item.name}
            </Link>
          );
        })}
      </nav>

      <div className="p-4 border-t border-[var(--color-outline-variant)]">
        <button
          onClick={logout}
          className="flex items-center gap-3 w-full px-4 py-3 text-body-md text-[var(--color-error)] hover:bg-[var(--color-error-container)] rounded transition-colors"
        >
          <LogOut size={20} />
          Cerrar Sesión
        </button>
      </div>
    </div>
  );
}
