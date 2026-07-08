'use client';

import React, { useEffect, useState } from 'react';
import { useAuth } from '@/context/AuthContext';
import { Activity, ShieldCheck, Users, Server, AlertTriangle } from 'lucide-react';
import { RolesService } from '@/services/roles.service';
import { UsersService } from '@/services/users.service';

export default function DashboardPage() {
  const { currentRole, roles } = useAuth();
  const [stats, setStats] = useState({ roles: 0, users: 0, activeServices: 4 });
  
  useEffect(() => {
    // Fetch some basic stats
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
  }, []);

  const activeRoleName = roles.find(r => r.id === currentRole)?.nombre || 'Unknown';

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
    </div>
  );
}
