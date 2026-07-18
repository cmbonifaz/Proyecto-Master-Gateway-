'use client';

import React, { useEffect, useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { UsersService, User } from '@/services/users.service';
import { RolesService, Role } from '@/services/roles.service';
import { Users, Plus, Trash2, Edit, Shield, X, Check } from 'lucide-react';
import { AuditDetails } from '@/components/ui/AuditDetails';

const userSchema = z.object({
  id: z.string().optional(),
  email: z.string().email("Correo inválido"),
  nombre: z.string().min(2, "Mínimo 2 caracteres"),
  password: z.string().optional().or(z.literal('')),
}).superRefine((val, ctx) => {
  // Si estamos creando un nuevo usuario (sin ID en el formulario)
  if (!val.id) {
    if (!val.password) {
      ctx.addIssue({ 
        code: z.ZodIssueCode.custom, 
        message: "La contraseña es obligatoria para nuevos usuarios", 
        path: ["password"] 
      });
      return;
    }
  }

  if (val.password) {
    if (val.password.length < 8) {
      ctx.addIssue({ code: z.ZodIssueCode.custom, message: "La contraseña debe tener al menos 8 caracteres", path: ["password"] });
    }
    if (!/[A-Z]/.test(val.password)) {
      ctx.addIssue({ code: z.ZodIssueCode.custom, message: "Debe contener al menos una mayúscula", path: ["password"] });
    }
    if (!/[a-z]/.test(val.password)) {
      ctx.addIssue({ code: z.ZodIssueCode.custom, message: "Debe contener al menos una minúscula", path: ["password"] });
    }
    if (!/[0-9]/.test(val.password)) {
      ctx.addIssue({ code: z.ZodIssueCode.custom, message: "Debe contener al menos un número", path: ["password"] });
    }
    if (!/[!@#$%^&*(),.?":{}|<>]/.test(val.password)) {
      ctx.addIssue({ code: z.ZodIssueCode.custom, message: "Debe contener al menos un carácter especial", path: ["password"] });
    }
  }
});

type UserFormValues = z.infer<typeof userSchema>;

const handleAxiosError = (err: any, defaultMsg: string) => {
  const detail = err.response?.data?.detail;
  if (typeof detail === 'string') {
    return detail;
  }
  if (Array.isArray(detail)) {
    return detail.map((d: any) => d.msg ? d.msg.replace(/^Value error, /, '') : JSON.stringify(d)).join(', ');
  }
  if (detail && typeof detail === 'object') {
    return JSON.stringify(detail);
  }
  if (typeof err.response?.data === 'string') {
    return err.response.data;
  }
  if (err.response?.data?.message) {
    return err.response.data.message;
  }
  return err.message || defaultMsg;
};

function RoleChip({ label, active, onToggle, loading }: { label: string; active: boolean; onToggle: () => void; loading?: boolean }) {
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

export default function UsersPage() {
  const [users, setUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [isFormOpen, setIsFormOpen] = useState(false);
  const [editingUserId, setEditingUserId] = useState<string | null>(null);
  const [rolesModal, setRolesModal] = useState<User | null>(null);
  const [allRoles, setAllRoles] = useState<Role[]>([]);
  const [toggling, setToggling] = useState<string | null>(null);

  const { register, handleSubmit, reset, setValue, watch, formState: { errors, isSubmitting } } = useForm<UserFormValues>({
    resolver: zodResolver(userSchema),
  });

  const formPassword = watch('password', '') || '';

  const passwordRequirements = [
    { label: 'Mínimo 8 caracteres', met: formPassword.length >= 8 },
    { label: 'Al menos una mayúscula', met: /[A-Z]/.test(formPassword) },
    { label: 'Al menos una minúscula', met: /[a-z]/.test(formPassword) },
    { label: 'Al menos un número', met: /[0-9]/.test(formPassword) },
    { label: 'Al menos un carácter especial (!@#$%^&...)', met: /[!@#$%^&*(),.?":{}|<>]/.test(formPassword) },
  ];

  const fetchUsers = async () => {
    setLoading(true);
    try {
      const data = await UsersService.getUsers();
      setUsers(data);
    } catch (e: any) {
      setError(handleAxiosError(e, 'Error cargando usuarios'));
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchUsers(); }, []);

  const openNewModal = () => {
    setError('');
    setEditingUserId(null);
    reset({ id: '', email: '', nombre: '', password: '' });
    setIsFormOpen(true);
  };

  const openEditModal = (user: User) => {
    setError('');
    setEditingUserId(user.id);
    reset({ id: user.id, email: user.email, nombre: user.nombre, password: '' });
    setIsFormOpen(true);
  };

  const openRolesModal = async (user: User) => {
    setRolesModal(user);
    try {
      const roles = await RolesService.getRoles();
      setAllRoles(roles);
    } catch (e: any) {
      setError('Error cargando roles');
    }
  };

  const isRoleAssigned = (roleId: string) =>
    rolesModal?.roles?.some((r: any) => r.id === roleId) ?? false;

  const toggleRole = async (roleId: string) => {
    if (!rolesModal) return;
    setToggling(roleId);
    try {
      if (isRoleAssigned(roleId)) {
        await RolesService.unassignUser(roleId, rolesModal.id);
      } else {
        await RolesService.assignUser(roleId, rolesModal.id);
      }
      // Refresh user data to get updated roles list
      const updatedUsers = await UsersService.getUsers();
      setUsers(updatedUsers);
      const updatedUser = updatedUsers.find((u: User) => u.id === rolesModal.id);
      if (updatedUser) setRolesModal(updatedUser);
    } catch (e: any) {
      setError(handleAxiosError(e, 'Error al cambiar rol'));
    } finally {
      setToggling(null);
    }
  };

  const onSubmit = async (data: UserFormValues) => {
    try {
      if (editingUserId) {
        const payload: any = { email: data.email, nombre: data.nombre };
        if (data.password) payload.password = data.password;
        await UsersService.updateUser(editingUserId, payload);
      } else {
        if (!data.password) throw new Error('La contraseña es obligatoria para nuevos usuarios');
        await UsersService.createUser({ email: data.email, nombre: data.nombre, password: data.password });
      }
      setIsFormOpen(false);
      reset();
      fetchUsers();
    } catch (e: any) {
      setError(handleAxiosError(e, 'Error guardando usuario'));
    }
  };

  const handleDelete = async (id: string) => {
    if (!confirm('¿Estás seguro de inactivar/eliminar este usuario?')) return;
    try {
      await UsersService.deleteUser(id);
      fetchUsers();
    } catch (e: any) {
      alert(handleAxiosError(e, 'Error eliminando usuario'));
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-headline-lg text-[var(--color-on-surface)] flex items-center gap-3">
          <Users size={32} className="text-[var(--color-primary)]" />
          Gestión de Usuarios
        </h1>
        <button onClick={openNewModal}
          className="bg-[var(--color-primary)] text-white px-4 py-2 rounded flex items-center gap-2 hover:bg-[#0f0f5c] transition-colors">
          <Plus size={20} /> Nuevo Usuario
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
              <th className="px-6 py-3 text-label-md text-[var(--color-on-surface-variant)] uppercase">Email</th>
              <th className="px-6 py-3 text-label-md text-[var(--color-on-surface-variant)] uppercase">Estado</th>
              <th className="px-6 py-3 text-label-md text-[var(--color-on-surface-variant)] uppercase">Roles</th>
              <th className="px-6 py-3 text-label-md text-[var(--color-on-surface-variant)] uppercase text-right">Acciones</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-[var(--color-outline-variant)]">
            {loading ? (
              <tr><td colSpan={5} className="px-6 py-8 text-center text-[var(--color-on-surface-variant)]">Cargando...</td></tr>
            ) : users.length === 0 ? (
              <tr><td colSpan={5} className="px-6 py-8 text-center text-[var(--color-on-surface-variant)]">No se encontraron usuarios</td></tr>
            ) : (
              users.map(user => (
                <tr key={user.id} className="hover:bg-[var(--color-surface-container-lowest)] transition-colors">
                  <td className="px-6 py-4">
                    <div className="text-body-md font-semibold text-[var(--color-primary)]">{user.nombre}</div>
                    <div className="text-xs text-[var(--color-on-surface-variant)] mt-1 font-mono">{user.id}</div>
                  </td>
                  <td className="px-6 py-4 text-body-md text-[var(--color-on-surface)]">{user.email}</td>
                  <td className="px-6 py-4">
                    <span className={`px-2 py-1 rounded-full text-xs font-bold ${user.estado === 'ACTIVO' ? 'bg-[#ccfbf1] text-[#115e59]' : 'bg-[#fee2e2] text-[#991b1b]'}`}>
                      {user.estado}
                    </span>
                  </td>
                  <td className="px-6 py-4 text-body-sm text-[var(--color-on-surface-variant)]">
                    {user.roles?.length > 0
                      ? user.roles.map((r: any) => (
                          <span key={r.id} className="inline-block bg-[var(--color-primary-container)] text-[var(--color-on-primary-container)] px-2 py-0.5 rounded text-xs mr-1 mb-1 font-semibold">
                            {r.nombre}
                          </span>
                        ))
                      : <span className="italic">Sin roles</span>
                    }
                  </td>
                  <td className="px-6 py-4 text-right space-x-1">
                    <AuditDetails data={user} title="Auditoría de Usuario" />
                    <button onClick={() => openRolesModal(user)} className="p-2 text-[var(--color-on-surface-variant)] hover:text-[var(--color-secondary)] hover:bg-[var(--color-secondary-container)] rounded transition-colors inline-flex items-center justify-center" title="Asignar roles">
                      <Shield size={18} />
                    </button>
                    <button onClick={() => openEditModal(user)} className="p-2 text-[var(--color-on-surface-variant)] hover:text-[var(--color-primary)] hover:bg-[var(--color-primary-container)] rounded transition-colors inline-flex items-center justify-center" title="Editar">
                      <Edit size={18} />
                    </button>
                    <button onClick={() => handleDelete(user.id)} className="p-2 text-[var(--color-on-surface-variant)] hover:text-[var(--color-error)] hover:bg-[var(--color-error-container)] rounded transition-colors inline-flex items-center justify-center" title="Eliminar/Inactivar">
                      <Trash2 size={18} />
                    </button>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      {/* ── Modal Crear / Editar Usuario ── */}
      {isFormOpen && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg shadow-elevation-2 w-full max-w-md border border-[var(--color-outline-variant)]">
            <div className="px-6 py-4 border-b border-[var(--color-outline-variant)] flex justify-between items-center">
              <h2 className="text-headline-sm text-[var(--color-on-surface)]">{editingUserId ? 'Editar Usuario' : 'Nuevo Usuario'}</h2>
              <button onClick={() => { setIsFormOpen(false); setError(''); }} className="text-[var(--color-on-surface-variant)] hover:text-[var(--color-on-surface)]">&times;</button>
            </div>
            <form onSubmit={handleSubmit(onSubmit)} className="p-6 space-y-4">
              <input type="hidden" {...register('id')} />
              {error && (
                <div className="bg-[var(--color-error-container)] text-[var(--color-on-error-container)] p-3 rounded text-body-sm border border-[#ffb4ab] flex justify-between items-center">
                  <span>{error}</span>
                  <button type="button" onClick={() => setError('')} className="font-bold ml-2">✕</button>
                </div>
              )}
              <div>
                <label className="block text-label-md text-[var(--color-on-surface)] mb-1">NOMBRE COMPLETO *</label>
                <input {...register('nombre')}
                  className={`w-full px-3 py-2 border rounded text-body-md focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)] ${errors.nombre ? 'border-[var(--color-error)]' : 'border-[var(--color-outline-variant)]'}`}
                  placeholder="Ej: Juan Pérez" />
                {errors.nombre && <p className="text-[var(--color-error)] text-body-sm mt-1">{errors.nombre.message}</p>}
              </div>
              <div>
                <label className="block text-label-md text-[var(--color-on-surface)] mb-1">CORREO ELECTRÓNICO *</label>
                <input type="email" {...register('email')}
                  className={`w-full px-3 py-2 border rounded text-body-md focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)] ${errors.email ? 'border-[var(--color-error)]' : 'border-[var(--color-outline-variant)]'}`}
                  placeholder="juan@gateway.com" />
                {errors.email && <p className="text-[var(--color-error)] text-body-sm mt-1">{errors.email.message}</p>}
              </div>
              <div>
                <label className="block text-label-md text-[var(--color-on-surface)] mb-1">
                  CONTRASEÑA {editingUserId && <span className="text-[var(--color-on-surface-variant)] font-normal normal-case">(dejar vacío para no cambiar)</span>}
                </label>
                <input type="password" {...register('password')}
                  className={`w-full px-3 py-2 border rounded text-body-md focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)] ${errors.password ? 'border-[var(--color-error)]' : 'border-[var(--color-outline-variant)]'}`}
                  placeholder="••••••••" />
                {errors.password && <p className="text-[var(--color-error)] text-body-sm mt-1">{errors.password.message}</p>}
                
                {/* Feedback visual de requerimientos */}
                {(!editingUserId || formPassword) && (
                  <div className="mt-2 space-y-1.5 bg-[var(--color-surface-container-low)] p-3 rounded-md border border-[var(--color-outline-variant)]">
                    <p className="text-[11px] font-semibold text-[var(--color-on-surface-variant)] uppercase tracking-wider mb-1">Criterios de Seguridad:</p>
                    {passwordRequirements.map((req, i) => (
                      <div key={i} className="flex items-center gap-2 text-body-sm transition-all duration-200">
                        {req.met ? (
                          <Check size={14} className="text-green-500 stroke-[3]" />
                        ) : (
                          <X size={14} className="text-[var(--color-outline)] opacity-50" />
                        )}
                        <span className={req.met ? 'text-green-800 font-medium' : 'text-[var(--color-on-surface-variant)] opacity-70'}>
                          {req.label}
                        </span>
                      </div>
                    ))}
                  </div>
                )}
              </div>
              <div className="flex justify-end gap-3 mt-6">
                <button type="button" onClick={() => { setIsFormOpen(false); setError(''); }}
                  className="px-4 py-2 border border-[var(--color-outline-variant)] text-[var(--color-on-surface)] rounded hover:bg-[var(--color-surface-container-low)]">
                  Cancelar
                </button>
                <button type="submit" disabled={isSubmitting}
                  className="px-4 py-2 bg-[var(--color-primary)] text-white rounded hover:bg-[#0f0f5c] disabled:opacity-50">
                  {isSubmitting ? 'Guardando...' : 'Guardar Usuario'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* ── Modal Asignación de Roles ── */}
      {rolesModal && (
        <div className="fixed inset-0 bg-black bg-opacity-60 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg shadow-elevation-2 w-full max-w-lg border border-[var(--color-outline-variant)]">
            <div className="px-6 py-4 border-b border-[var(--color-outline-variant)] flex justify-between items-center">
              <div>
                <h2 className="text-headline-sm text-[var(--color-on-surface)] flex items-center gap-2">
                  <Shield size={20} className="text-[var(--color-primary)]" />
                  Asignar Roles
                </h2>
                <p className="text-body-sm text-[var(--color-on-surface-variant)] mt-0.5">
                  Usuario: <span className="font-semibold text-[var(--color-primary)]">{rolesModal.nombre}</span>
                </p>
              </div>
              <button onClick={() => setRolesModal(null)} className="p-2 rounded hover:bg-[var(--color-surface-container-low)] text-[var(--color-on-surface-variant)]">
                <X size={20} />
              </button>
            </div>
            <div className="p-6">
              <p className="text-body-sm text-[var(--color-on-surface-variant)] mb-4">
                Selecciona los roles que debe tener este usuario. Los cambios se aplican inmediatamente.
              </p>
              <div className="flex flex-wrap gap-2">
                {allRoles.length === 0
                  ? <p className="text-body-sm italic text-[var(--color-on-surface-variant)]">No hay roles disponibles.</p>
                  : allRoles.map(role => (
                      <RoleChip
                        key={role.id}
                        label={role.nombre}
                        active={isRoleAssigned(role.id)}
                        onToggle={() => toggleRole(role.id)}
                        loading={toggling === role.id}
                      />
                    ))
                }
              </div>
            </div>
            <div className="px-6 py-4 border-t border-[var(--color-outline-variant)] flex justify-end">
              <button onClick={() => setRolesModal(null)}
                className="px-4 py-2 bg-[var(--color-primary)] text-white rounded hover:bg-[#0f0f5c] transition-colors">
                Cerrar
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
