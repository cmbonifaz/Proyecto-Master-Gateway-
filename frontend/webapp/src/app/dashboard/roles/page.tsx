'use client';

import React, { useEffect, useState, useCallback } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { RolesService, Role } from '@/services/roles.service';
import { UsersService, User } from '@/services/users.service';
import { ModulesService, Module } from '@/services/modules.service';
import { MenusService, Menu } from '@/services/menus.service';
import { Shield, Plus, Trash2, Settings, Users, Layers, Menu as MenuIcon, X, Check } from 'lucide-react';

const roleSchema = z.object({
  nombre: z.string().min(3, "Mínimo 3 caracteres").regex(/^[A-Z0-9_]+$/, "Solo mayúsculas, números y guiones bajos"),
  descripcion: z.string().optional(),
});

type RoleFormValues = z.infer<typeof roleSchema>;
type PermTab = 'users' | 'modules' | 'menus';

interface RoleWithRelations extends Role {
  users?: User[];
  modules?: Module[];
  menus?: Menu[];
}

function ToggleChip({ label, active, onToggle, loading }: { label: string; active: boolean; onToggle: () => void; loading?: boolean }) {
  return (
    <button
      type="button"
      onClick={onToggle}
      disabled={loading}
      className={`flex items-center gap-2 px-3 py-2 rounded-lg border text-body-sm transition-all ${
        active
          ? 'bg-[var(--color-primary)] text-white border-[var(--color-primary)]'
          : 'bg-white text-[var(--color-on-surface)] border-[var(--color-outline-variant)] hover:bg-[var(--color-surface-container-low)]'
      } ${loading ? 'opacity-50 cursor-wait' : ''}`}
    >
      {active ? <Check size={14} /> : <Plus size={14} />}
      {label}
    </button>
  );
}

export default function RolesPage() {
  const [roles, setRoles] = useState<Role[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [isCreateOpen, setIsCreateOpen] = useState(false);
  const [permRole, setPermRole] = useState<RoleWithRelations | null>(null);
  const [permTab, setPermTab] = useState<PermTab>('users');
  const [allUsers, setAllUsers] = useState<User[]>([]);
  const [allModules, setAllModules] = useState<Module[]>([]);
  const [allMenus, setAllMenus] = useState<Menu[]>([]);
  const [toggling, setToggling] = useState<string | null>(null);

  const { register, handleSubmit, reset, formState: { errors, isSubmitting } } = useForm<RoleFormValues>({
    resolver: zodResolver(roleSchema),
  });

  const fetchRoles = async () => {
    setLoading(true);
    try {
      const data = await RolesService.getRoles();
      setRoles(data);
    } catch (e: any) {
      setError(e.response?.data?.detail || 'Error cargando roles');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchRoles(); }, []);

  const openPermModal = async (role: Role) => {
    setPermRole(role);
    setPermTab('users');
    try {
      const [users, modules, menus, permissions] = await Promise.all([
        UsersService.getUsers(),
        ModulesService.getModules(),
        MenusService.getMenus(),
        RolesService.getRolePermissions(role.id),
      ]);
      setAllUsers(users);
      setAllModules(modules);
      setAllMenus(menus);
      setPermRole({ ...role, ...permissions });
    } catch (e: any) {
      setError('Error cargando datos de permisos');
    }
  };

  const isUserAssigned = (userId: string) =>
    permRole?.users?.some((u: any) => u.id === userId) ?? false;
  const isModuleAssigned = (moduleId: string) =>
    permRole?.modules?.some((m: any) => m.id === moduleId) ?? false;
  const isMenuAssigned = (menuId: string) =>
    permRole?.menus?.some((m: any) => m.id === menuId) ?? false;

  const toggleUser = async (userId: string) => {
    if (!permRole) return;
    setToggling(userId);
    try {
      if (isUserAssigned(userId)) {
        await RolesService.unassignUser(permRole.id, userId);
      } else {
        await RolesService.assignUser(permRole.id, userId);
      }
      const permissions = await RolesService.getRolePermissions(permRole.id);
      setPermRole(prev => prev ? { ...prev, ...permissions } : null);
    } catch (e: any) {
      setError(e.response?.data?.detail || 'Error al cambiar asignación');
    } finally {
      setToggling(null);
    }
  };

  const toggleModule = async (moduleId: string) => {
    if (!permRole) return;
    setToggling(moduleId);
    try {
      if (isModuleAssigned(moduleId)) {
        await RolesService.unassignModule(permRole.id, moduleId);
      } else {
        await RolesService.assignModule(permRole.id, moduleId);
      }
      const permissions = await RolesService.getRolePermissions(permRole.id);
      setPermRole(prev => prev ? { ...prev, ...permissions } : null);
    } catch (e: any) {
      setError(e.response?.data?.detail || 'Error al cambiar módulo');
    } finally {
      setToggling(null);
    }
  };

  const toggleMenu = async (menuId: string) => {
    if (!permRole) return;
    setToggling(menuId);
    try {
      if (isMenuAssigned(menuId)) {
        await RolesService.unassignMenu(permRole.id, menuId);
      } else {
        await RolesService.assignMenu(permRole.id, menuId);
      }
      const permissions = await RolesService.getRolePermissions(permRole.id);
      setPermRole(prev => prev ? { ...prev, ...permissions } : null);
    } catch (e: any) {
      setError(e.response?.data?.detail || 'Error al cambiar menú');
    } finally {
      setToggling(null);
    }
  };

  const onSubmit = async (data: RoleFormValues) => {
    try {
      await RolesService.createRole(data);
      setIsCreateOpen(false);
      reset();
      fetchRoles();
    } catch (e: any) {
      setError(e.response?.data?.detail || 'Error creando rol');
    }
  };

  const handleDelete = async (id: string) => {
    if (!confirm('¿Estás seguro de eliminar este rol?')) return;
    try {
      await RolesService.deleteRole(id);
      fetchRoles();
    } catch (e: any) {
      alert(e.response?.data?.detail || 'Error eliminando rol');
    }
  };

  const tabs: { key: PermTab; label: string; icon: React.ElementType }[] = [
    { key: 'users', label: 'Usuarios', icon: Users },
    { key: 'modules', label: 'Módulos', icon: Layers },
    { key: 'menus', label: 'Menús', icon: MenuIcon },
  ];

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-headline-lg text-[var(--color-on-surface)] flex items-center gap-3">
          <Shield size={32} className="text-[var(--color-primary)]" />
          Gestión de Roles
        </h1>
        <button
          onClick={() => setIsCreateOpen(true)}
          className="bg-[var(--color-primary)] text-white px-4 py-2 rounded flex items-center gap-2 hover:bg-[#0f0f5c] transition-colors"
        >
          <Plus size={20} /> Nuevo Rol
        </button>
      </div>

      {error && (
        <div className="bg-[var(--color-error-container)] text-[var(--color-on-error-container)] p-4 rounded text-body-md border border-[#ffb4ab] flex justify-between">
          {error}
          <button onClick={() => setError('')} className="font-bold">✕</button>
        </div>
      )}

      <div className="bg-white rounded-lg shadow-elevation-1 border border-[var(--color-outline-variant)] overflow-hidden">
        <table className="w-full text-left border-collapse">
          <thead>
            <tr className="bg-[var(--color-surface-container-low)] border-b border-[var(--color-outline-variant)]">
              <th className="px-6 py-3 text-label-md text-[var(--color-on-surface-variant)] uppercase">Nombre</th>
              <th className="px-6 py-3 text-label-md text-[var(--color-on-surface-variant)] uppercase">Descripción</th>
              <th className="px-6 py-3 text-label-md text-[var(--color-on-surface-variant)] uppercase">Estado</th>
              <th className="px-6 py-3 text-label-md text-[var(--color-on-surface-variant)] uppercase text-right">Acciones</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-[var(--color-outline-variant)]">
            {loading ? (
              <tr><td colSpan={4} className="px-6 py-8 text-center text-[var(--color-on-surface-variant)]">Cargando...</td></tr>
            ) : roles.length === 0 ? (
              <tr><td colSpan={4} className="px-6 py-8 text-center text-[var(--color-on-surface-variant)]">No se encontraron roles</td></tr>
            ) : (
              roles.map(role => (
                <tr key={role.id} className="hover:bg-[var(--color-surface-container-lowest)] transition-colors">
                  <td className="px-6 py-4">
                    <div className="text-body-md font-semibold text-[var(--color-primary)]">{role.nombre}</div>
                    <div className="text-xs text-[var(--color-on-surface-variant)] mt-1 font-mono">{role.id}</div>
                  </td>
                  <td className="px-6 py-4 text-body-md text-[var(--color-on-surface)]">{role.descripcion || <span className="italic text-[var(--color-on-surface-variant)]">Sin descripción</span>}</td>
                  <td className="px-6 py-4">
                    <span className="bg-[#ccfbf1] text-[#115e59] px-2 py-1 rounded-full text-xs font-bold">{role.estado}</span>
                  </td>
                  <td className="px-6 py-4 text-right space-x-2">
                    <button
                      onClick={() => openPermModal(role)}
                      className="p-2 text-[var(--color-on-surface-variant)] hover:text-[var(--color-primary)] hover:bg-[var(--color-primary-container)] rounded transition-colors"
                      title="Gestionar permisos (usuarios, módulos, menús)"
                    >
                      <Settings size={18} />
                    </button>
                    <button
                      onClick={() => handleDelete(role.id)}
                      className="p-2 text-[var(--color-on-surface-variant)] hover:text-[var(--color-error)] hover:bg-[var(--color-error-container)] rounded transition-colors"
                      title="Eliminar"
                    >
                      <Trash2 size={18} />
                    </button>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      {/* ── Modal Crear Rol ── */}
      {isCreateOpen && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg shadow-elevation-2 w-full max-w-md border border-[var(--color-outline-variant)]">
            <div className="px-6 py-4 border-b border-[var(--color-outline-variant)] flex justify-between items-center">
              <h2 className="text-headline-sm text-[var(--color-on-surface)]">Crear Nuevo Rol</h2>
              <button onClick={() => setIsCreateOpen(false)} className="text-[var(--color-on-surface-variant)] hover:text-[var(--color-on-surface)]">&times;</button>
            </div>
            <form onSubmit={handleSubmit(onSubmit)} className="p-6 space-y-4">
              <div>
                <label className="block text-label-md text-[var(--color-on-surface)] mb-1">NOMBRE (MAYÚSCULAS)</label>
                <input
                  {...register('nombre')}
                  className={`w-full px-3 py-2 border rounded text-body-md focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)] ${errors.nombre ? 'border-[var(--color-error)]' : 'border-[var(--color-outline-variant)]'}`}
                  placeholder="EJ: SUPER_ADMIN"
                  onChange={(e) => {
                    e.target.value = e.target.value.toUpperCase().replace(/\s+/g, '_');
                    register('nombre').onChange(e);
                  }}
                />
                {errors.nombre && <p className="text-[var(--color-error)] text-body-sm mt-1">{errors.nombre.message}</p>}
              </div>
              <div>
                <label className="block text-label-md text-[var(--color-on-surface)] mb-1">DESCRIPCIÓN (OPCIONAL)</label>
                <textarea
                  {...register('descripcion')}
                  className="w-full px-3 py-2 border border-[var(--color-outline-variant)] rounded text-body-md focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]"
                  placeholder="Descripción del propósito de este rol"
                  rows={3}
                />
              </div>
              <div className="flex justify-end gap-3 mt-6">
                <button type="button" onClick={() => setIsCreateOpen(false)}
                  className="px-4 py-2 border border-[var(--color-outline-variant)] text-[var(--color-on-surface)] rounded hover:bg-[var(--color-surface-container-low)]">
                  Cancelar
                </button>
                <button type="submit" disabled={isSubmitting}
                  className="px-4 py-2 bg-[var(--color-primary)] text-white rounded hover:bg-[#0f0f5c] disabled:opacity-50">
                  {isSubmitting ? 'Guardando...' : 'Crear Rol'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* ── Modal Gestión de Permisos ── */}
      {permRole && (
        <div className="fixed inset-0 bg-black bg-opacity-60 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg shadow-elevation-2 w-full max-w-2xl border border-[var(--color-outline-variant)] max-h-[85vh] flex flex-col">
            {/* Header */}
            <div className="px-6 py-4 border-b border-[var(--color-outline-variant)] flex justify-between items-center flex-shrink-0">
              <div>
                <h2 className="text-headline-sm text-[var(--color-on-surface)] flex items-center gap-2">
                  <Settings size={20} className="text-[var(--color-primary)]" />
                  Gestionar Permisos
                </h2>
                <p className="text-body-sm text-[var(--color-on-surface-variant)] mt-0.5">
                  Rol: <span className="font-semibold text-[var(--color-primary)]">{permRole.nombre}</span>
                </p>
              </div>
              <button onClick={() => setPermRole(null)} className="p-2 rounded hover:bg-[var(--color-surface-container-low)] text-[var(--color-on-surface-variant)]">
                <X size={20} />
              </button>
            </div>

            {/* Tabs */}
            <div className="flex border-b border-[var(--color-outline-variant)] flex-shrink-0">
              {tabs.map(tab => (
                <button
                  key={tab.key}
                  onClick={() => setPermTab(tab.key)}
                  className={`flex items-center gap-2 px-6 py-3 text-body-md transition-colors border-b-2 -mb-px ${
                    permTab === tab.key
                      ? 'border-[var(--color-primary)] text-[var(--color-primary)] font-semibold'
                      : 'border-transparent text-[var(--color-on-surface-variant)] hover:text-[var(--color-on-surface)]'
                  }`}
                >
                  <tab.icon size={16} />
                  {tab.label}
                </button>
              ))}
            </div>

            {/* Tab Content */}
            <div className="p-6 overflow-y-auto flex-1">
              {permTab === 'users' && (
                <div>
                  <p className="text-body-sm text-[var(--color-on-surface-variant)] mb-4">
                    Selecciona los usuarios que deben tener el rol <strong>{permRole.nombre}</strong>.
                  </p>
                  <div className="flex flex-wrap gap-2">
                    {allUsers.length === 0 && <p className="text-body-sm text-[var(--color-on-surface-variant)] italic">No hay usuarios disponibles.</p>}
                    {allUsers.map(user => (
                      <ToggleChip
                        key={user.id}
                        label={user.nombre || user.email}
                        active={isUserAssigned(user.id)}
                        onToggle={() => toggleUser(user.id)}
                        loading={toggling === user.id}
                      />
                    ))}
                  </div>
                </div>
              )}

              {permTab === 'modules' && (
                <div>
                  <p className="text-body-sm text-[var(--color-on-surface-variant)] mb-4">
                    Selecciona los módulos accesibles para el rol <strong>{permRole.nombre}</strong>.
                  </p>
                  <div className="flex flex-wrap gap-2">
                    {allModules.length === 0 && <p className="text-body-sm text-[var(--color-on-surface-variant)] italic">No hay módulos disponibles.</p>}
                    {allModules.map(mod => (
                      <ToggleChip
                        key={mod.id}
                        label={mod.nombre}
                        active={isModuleAssigned(mod.id)}
                        onToggle={() => toggleModule(mod.id)}
                        loading={toggling === mod.id}
                      />
                    ))}
                  </div>
                </div>
              )}

              {permTab === 'menus' && (
                <div>
                  <p className="text-body-sm text-[var(--color-on-surface-variant)] mb-4">
                    Selecciona los ítems de menú visibles para el rol <strong>{permRole.nombre}</strong>.
                  </p>
                  <div className="flex flex-wrap gap-2">
                    {allMenus.length === 0 && <p className="text-body-sm text-[var(--color-on-surface-variant)] italic">No hay menús disponibles.</p>}
                    {allMenus.map(menu => (
                      <ToggleChip
                        key={menu.id}
                        label={menu.parent_id ? `↳ ${menu.texto}` : menu.texto}
                        active={isMenuAssigned(menu.id)}
                        onToggle={() => toggleMenu(menu.id)}
                        loading={toggling === menu.id}
                      />
                    ))}
                  </div>
                </div>
              )}
            </div>

            <div className="px-6 py-4 border-t border-[var(--color-outline-variant)] flex justify-end flex-shrink-0">
              <button
                onClick={() => setPermRole(null)}
                className="px-4 py-2 bg-[var(--color-primary)] text-white rounded hover:bg-[#0f0f5c] transition-colors"
              >
                Cerrar
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
