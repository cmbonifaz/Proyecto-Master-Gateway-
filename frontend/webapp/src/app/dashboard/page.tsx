'use client';

import React, { useEffect, useState } from 'react';
import { useAuth } from '@/context/AuthContext';
import { Activity, ShieldCheck, Users, Server, AlertTriangle, Layers, ChevronRight } from 'lucide-react';
import { RolesService } from '@/services/roles.service';
import { UsersService } from '@/services/users.service';
import { Module } from '@/services/modules.service';
import Link from 'next/link';

export default function DashboardPage() {
  const { currentRole, roles } = useAuth();
  const [stats, setStats] = useState({ roles: 0, users: 0, activeServices: 4 });
  const [userModules, setUserModules] = useState<Module[]>([]);
  const activeRoleName = roles.find(r => r.id === currentRole)?.nombre || 'Unknown';
  const isAdmin = activeRoleName.toLowerCase() === 'admin' || activeRoleName.toLowerCase() === 'administrador';

  useEffect(() => {
    // Si es administrador, carga estadísticas
    if (isAdmin) {
      const fetchStats = async () => {
        try {
          const [rolesData, usersData] = await Promise.all([
            RolesService.getRoles(),
            UsersService.getUsers()
          ]);
          setStats(prev => ({
            ...prev,
            roles: rolesData.length,
            users: usersData.length
          }));
        } catch (e) {
          console.error("Failed to load dashboard stats", e);
        }
      };
      fetchStats();
    }
    
    // Carga los módulos permitidos para el rol activo (tanto para admin como normales)
    if (currentRole) {
      const fetchModules = async () => {
        try {
          const perms = await RolesService.getRolePermissions(currentRole);
          setUserModules(perms.modules || []);
        } catch (e) {
          console.error("Failed to load user modules", e);
        }
      };
      fetchModules();
    }
  }, [isAdmin, currentRole]);

  if (!isAdmin) {
    return (
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <h1 className="text-headline-lg text-[var(--color-on-surface)]">Bienvenido al Gateway</h1>
          <div className="bg-[var(--color-primary-container)] text-[var(--color-on-primary-container)] px-4 py-2 rounded-full text-label-md flex items-center gap-2">
            <ShieldCheck size={16} />
            Rol: {activeRoleName}
          </div>
        </div>

        <p className="text-body-lg text-[var(--color-on-surface-variant)] mb-8">
          Selecciona uno de los módulos a los que tienes acceso:
        </p>

        {userModules.length === 0 ? (
          <div className="bg-[var(--color-surface-container-low)] p-8 rounded-lg text-center border border-[var(--color-outline-variant)]">
            <Layers size={48} className="mx-auto text-[var(--color-on-surface-variant)] opacity-50 mb-4" />
            <p className="text-body-lg text-[var(--color-on-surface-variant)]">No tienes módulos asignados.</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {userModules.map(mod => (
              <Link href={`/dashboard`} key={mod.id} className="block group">
                <div className="bg-white p-6 rounded-lg shadow-elevation-1 hover:shadow-elevation-3 transition-all border border-[var(--color-outline-variant)] hover:border-[var(--color-primary)] h-full flex flex-col">
                  <div className="w-12 h-12 bg-[var(--color-secondary-container)] text-[var(--color-on-secondary-container)] rounded-xl flex items-center justify-center mb-4 group-hover:scale-110 transition-transform">
                    <Layers size={24} />
                  </div>
                  <h3 className="text-title-lg text-[var(--color-on-surface)] font-bold mb-2">{mod.nombre}</h3>
                  <p className="text-body-md text-[var(--color-on-surface-variant)] flex-1">{mod.descripcion || 'Sin descripción'}</p>
                  <div className="mt-4 flex items-center text-[var(--color-primary)] font-medium text-label-lg group-hover:translate-x-2 transition-transform">
                    Acceder al módulo <ChevronRight size={18} className="ml-1" />
                  </div>
                </div>
              </Link>
            ))}
          </div>
        )}
      </div>
    );
  }

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
              <Server size={24} />
            </div>
            <div>
              <p className="text-label-md text-[var(--color-on-surface-variant)] uppercase">Servicios Activos</p>
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
          <Layers className="text-[var(--color-primary)]" /> Módulos Asignados
        </h2>
        {userModules.length === 0 ? (
          <p className="text-body-md text-[var(--color-on-surface-variant)]">No tienes módulos asignados.</p>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {userModules.map(mod => (
              <div key={mod.id} className="bg-white p-5 rounded-lg shadow-elevation-1 border border-[var(--color-outline-variant)]">
                <h3 className="text-title-md text-[var(--color-on-surface)] font-bold mb-1 truncate">{mod.nombre}</h3>
                <p className="text-body-sm text-[var(--color-on-surface-variant)] line-clamp-2">{mod.descripcion || 'Sin descripción'}</p>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
