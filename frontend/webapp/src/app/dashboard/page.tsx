'use client';

import React, { useEffect, useState } from 'react';
import { useAuth } from '@/context/AuthContext';
import {
  Activity, ShieldCheck, Users, Server, AlertTriangle, Layers,
  ChevronRight, Package, BarChart2, UserCheck,
} from 'lucide-react';
import { RolesService } from '@/services/roles.service';
import { UsersService } from '@/services/users.service';
import { Module } from '@/services/modules.service';
import Link from 'next/link';

const MODULE_ICON_COLORS = [
  { bg: 'bg-blue-100',   text: 'text-blue-600',   border: 'border-blue-200',   hover: 'hover:border-blue-400' },
  { bg: 'bg-purple-100', text: 'text-purple-600',  border: 'border-purple-200', hover: 'hover:border-purple-400' },
  { bg: 'bg-emerald-100',text: 'text-emerald-600', border: 'border-emerald-200',hover: 'hover:border-emerald-400' },
  { bg: 'bg-orange-100', text: 'text-orange-600',  border: 'border-orange-200', hover: 'hover:border-orange-400' },
  { bg: 'bg-rose-100',   text: 'text-rose-600',    border: 'border-rose-200',   hover: 'hover:border-rose-400' },
  { bg: 'bg-cyan-100',   text: 'text-cyan-600',    border: 'border-cyan-200',   hover: 'hover:border-cyan-400' },
];

const MODULE_ICONS = [Layers, Package, BarChart2, UserCheck, ShieldCheck, Server];

export default function DashboardPage() {
  const { currentRole, roles } = useAuth();
  const [stats, setStats] = useState({ roles: 0, users: 0, activeServices: 0 });
  const [userModules, setUserModules] = useState<Module[]>([]);
  const [loadingModules, setLoadingModules] = useState(true);
  const activeRoleName = roles.find(r => r.id === currentRole)?.nombre || '';
  const isAdmin = activeRoleName.toLowerCase() === 'admin' || activeRoleName.toLowerCase() === 'administrador';

  useEffect(() => {
    if (isAdmin) {
      const fetchStats = async () => {
        try {
          const { ModulesService } = await import('@/services/modules.service');
          const [rolesData, usersData, modulesData] = await Promise.all([
            RolesService.getRoles(),
            UsersService.getUsers(),
            ModulesService.getModules()
          ]);
          setStats(prev => ({
            ...prev,
            roles: rolesData.length,
            users: usersData.length,
            activeServices: modulesData.length
          }));
        } catch (e) {
          console.error("Failed to load dashboard stats", e);
        }
      };
      fetchStats();
    }

    if (currentRole) {
      const fetchModules = async () => {
        try {
          setLoadingModules(true);
          const perms = await RolesService.getRolePermissions(currentRole);
          setUserModules(perms.modules || []);
        } catch (e) {
          console.error("Failed to load user modules", e);
        } finally {
          setLoadingModules(false);
        }
      };
      fetchModules();
    }
  }, [isAdmin, currentRole]);

  // ── Vista para usuarios NO administradores ─────────────────────────────────
  if (!isAdmin) {
    return (
      <div className="min-h-[calc(100vh-4rem)] flex flex-col">
        {/* Header */}
        <div className="mb-10">
          <h1 className="text-headline-lg text-[var(--color-on-surface)] font-bold">
            Bienvenido al Gateway
          </h1>
          <p className="text-body-lg text-[var(--color-on-surface-variant)] mt-2">
            Selecciona un módulo para comenzar a trabajar.
          </p>
        </div>

        {loadingModules ? (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
            {[1, 2, 3].map(i => (
              <div key={i} className="bg-white rounded-2xl p-6 border border-[var(--color-outline-variant)] animate-pulse">
                <div className="w-14 h-14 rounded-xl bg-gray-100 mb-4" />
                <div className="h-5 bg-gray-100 rounded w-3/4 mb-2" />
                <div className="h-4 bg-gray-100 rounded w-full mb-1" />
                <div className="h-4 bg-gray-100 rounded w-5/6" />
              </div>
            ))}
          </div>
        ) : userModules.length === 0 ? (
          <div className="flex-1 flex flex-col items-center justify-center text-center py-20">
            <div className="w-24 h-24 bg-[var(--color-surface-container-low)] rounded-full flex items-center justify-center mb-6">
              <Layers size={48} className="text-[var(--color-on-surface-variant)] opacity-40" />
            </div>
            <h2 className="text-title-lg text-[var(--color-on-surface)] font-semibold mb-2">Sin módulos asignados</h2>
            <p className="text-body-md text-[var(--color-on-surface-variant)] max-w-sm">
              Tu rol aún no tiene módulos asignados. Contacta a un administrador para obtener acceso.
            </p>
          </div>
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
            {userModules.map((mod, index) => {
              const colors = MODULE_ICON_COLORS[index % MODULE_ICON_COLORS.length];
              const IconCmp = MODULE_ICONS[index % MODULE_ICONS.length];
              return (
                <Link
                  href={`/dashboard/module/${mod.id}`}
                  key={mod.id}
                  className="group block"
                >
                  <div
                    className={`bg-white rounded-2xl p-6 border-2 ${colors.border} ${colors.hover} shadow-sm hover:shadow-md transition-all duration-200 h-full flex flex-col cursor-pointer`}
                  >
                    <div className={`w-14 h-14 ${colors.bg} ${colors.text} rounded-xl flex items-center justify-center mb-5 group-hover:scale-110 transition-transform duration-200`}>
                      <IconCmp size={28} />
                    </div>

                    <h3 className="text-title-lg text-[var(--color-on-surface)] font-bold mb-2 group-hover:text-[var(--color-primary)] transition-colors">
                      {mod.nombre}
                    </h3>
                    <p className="text-body-md text-[var(--color-on-surface-variant)] flex-1 line-clamp-2">
                      {mod.descripcion || 'Sin descripción disponible.'}
                    </p>

                    <div className={`mt-5 flex items-center gap-1 text-sm font-semibold ${colors.text} group-hover:gap-2 transition-all`}>
                      Acceder al módulo
                      <ChevronRight size={16} className="group-hover:translate-x-1 transition-transform" />
                    </div>
                  </div>
                </Link>
              );
            })}
          </div>
        )}
      </div>
    );
  }

  // ── Vista para ADMIN ───────────────────────────────────────────────────────
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-headline-lg text-[var(--color-on-surface)]">Master Gateway Overview</h1>
        <div className="bg-[var(--color-tertiary-container)] text-[var(--color-on-tertiary-container)] px-4 py-2 rounded-full text-label-md flex items-center gap-2">
          <ShieldCheck size={16} />
          ZERO TRUST SECURE
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-white p-6 rounded-lg shadow-elevation-1 hover:shadow-elevation-2 transition-shadow border border-[var(--color-outline-variant)]">
          <div className="flex items-center gap-4">
            <div className="w-12 h-12 bg-[var(--color-primary-fixed)] text-[var(--color-on-primary-fixed)] rounded flex items-center justify-center">
              <Users size={24} />
            </div>
            <div>
              <p className="text-label-md text-[var(--color-on-surface-variant)] uppercase">Usuarios Totales</p>
              <h2 className="text-headline-lg text-[var(--color-on-surface)] mt-1">{stats.users}</h2>
            </div>
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow-elevation-1 hover:shadow-elevation-2 transition-shadow border border-[var(--color-outline-variant)]">
          <div className="flex items-center gap-4">
            <div className="w-12 h-12 bg-[var(--color-secondary-fixed)] text-[var(--color-on-secondary-fixed)] rounded flex items-center justify-center">
              <ShieldCheck size={24} />
            </div>
            <div>
              <p className="text-label-md text-[var(--color-on-surface-variant)] uppercase">Roles del Sistema</p>
              <h2 className="text-headline-lg text-[var(--color-on-surface)] mt-1">{stats.roles}</h2>
            </div>
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow-elevation-1 hover:shadow-elevation-2 transition-shadow border border-[var(--color-outline-variant)]">
          <div className="flex items-center gap-4">
            <div className="w-12 h-12 bg-[var(--color-tertiary-fixed)] text-[var(--color-on-tertiary-fixed)] rounded flex items-center justify-center">
              <Layers size={24} />
            </div>
            <div>
              <p className="text-label-md text-[var(--color-on-surface-variant)] uppercase">Módulos Activos</p>
              <h2 className="text-headline-lg text-[var(--color-on-surface)] mt-1">{stats.activeServices}</h2>
            </div>
          </div>
        </div>
      </div>

      <div className="mt-8 bg-white rounded-lg shadow-elevation-1 border border-[var(--color-outline-variant)] overflow-hidden">
        <div className="p-4 border-b border-[var(--color-outline-variant)] bg-[var(--color-surface-container-low)] flex justify-between items-center">
          <h3 className="text-headline-sm text-[var(--color-on-surface)]">Estado de la Sesión Actual</h3>
          <div className="flex items-center gap-2 text-body-sm bg-[var(--color-surface-variant)] px-3 py-1 rounded text-[var(--color-on-surface-variant)]">
            <Activity size={14} /> Activo
          </div>
        </div>
        <div className="p-6">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <p className="text-label-md text-[var(--color-on-surface-variant)]">ROL ACTIVO</p>
              <p className="text-body-lg font-mono text-[var(--color-primary)] mt-1">{activeRoleName}</p>
            </div>
            <div>
              <p className="text-label-md text-[var(--color-on-surface-variant)]">POLÍTICA DE ACCESO</p>
              <p className="text-body-lg text-[var(--color-on-surface)] mt-1">Deny by Default</p>
            </div>
          </div>

          <div className="mt-6 p-4 bg-[var(--color-error-container)] text-[var(--color-on-error-container)] rounded flex items-start gap-3 border border-[#ffb4ab]">
            <AlertTriangle size={20} className="mt-0.5 flex-shrink-0" />
            <div>
              <p className="text-label-md font-bold mb-1">AUDITORÍA DE SEGURIDAD</p>
              <p className="text-body-sm">
                Las acciones realizadas bajo este rol están siendo registradas.
                Los privilegios otorgados son estrictamente para fines de administración.
              </p>
            </div>
          </div>
        </div>
      </div>

      <div className="mt-8">
        <h2 className="text-title-lg text-[var(--color-on-surface)] mb-4 font-bold flex items-center gap-2">
          <Layers className="text-[var(--color-primary)]" /> Módulos del Sistema
        </h2>
        {userModules.length === 0 ? (
          <p className="text-body-md text-[var(--color-on-surface-variant)]">No hay módulos registrados.</p>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {userModules.map(mod => (
              <Link href={`/dashboard/module/${mod.id}`} key={mod.id}>
                <div className="bg-white p-5 rounded-lg shadow-elevation-1 border border-[var(--color-outline-variant)] hover:border-[var(--color-primary)] hover:shadow-elevation-2 transition-all cursor-pointer">
                  <h3 className="text-title-md text-[var(--color-on-surface)] font-bold mb-1 truncate">{mod.nombre}</h3>
                  <p className="text-body-sm text-[var(--color-on-surface-variant)] line-clamp-2">{mod.descripcion || 'Sin descripción'}</p>
                </div>
              </Link>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
