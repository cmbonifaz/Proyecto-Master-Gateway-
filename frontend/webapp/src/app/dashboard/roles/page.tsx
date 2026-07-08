'use client';

import React, { useEffect, useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { RolesService, Role } from '@/services/roles.service';
import { Shield, Plus, Trash2, Edit } from 'lucide-react';

const roleSchema = z.object({
  nombre: z.string().min(3, "Mínimo 3 caracteres").regex(/^[A-Z0-9_]+$/, "Solo mayúsculas, números y guiones bajos"),
  descripcion: z.string().optional(),
});

type RoleFormValues = z.infer<typeof roleSchema>;

export default function RolesPage() {
  const [roles, setRoles] = useState<Role[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [isModalOpen, setIsModalOpen] = useState(false);

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

  useEffect(() => {
    fetchRoles();
  }, []);

  const onSubmit = async (data: RoleFormValues) => {
    try {
      await RolesService.createRole(data);
      setIsModalOpen(false);
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

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-headline-lg text-[var(--color-on-surface)] flex items-center gap-3">
          <Shield size={32} className="text-[var(--color-primary)]" />
          Gestión de Roles
        </h1>
        <button
          onClick={() => setIsModalOpen(true)}
          className="bg-[var(--color-primary)] text-white px-4 py-2 rounded flex items-center gap-2 hover:bg-[#0f0f5c] transition-colors"
        >
          <Plus size={20} /> Nuevo Rol
        </button>
      </div>

      {error && (
        <div className="bg-[var(--color-error-container)] text-[var(--color-on-error-container)] p-4 rounded text-body-md border border-[#ffb4ab]">
          {error}
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
              <tr>
                <td colSpan={4} className="px-6 py-8 text-center text-[var(--color-on-surface-variant)]">Cargando...</td>
              </tr>
            ) : roles.length === 0 ? (
              <tr>
                <td colSpan={4} className="px-6 py-8 text-center text-[var(--color-on-surface-variant)]">No se encontraron roles</td>
              </tr>
            ) : (
              roles.map(role => (
                <tr key={role.id} className="hover:bg-[var(--color-surface-container-lowest)] transition-colors">
                  <td className="px-6 py-4">
                    <div className="text-body-md font-semibold text-[var(--color-primary)]">{role.nombre}</div>
                    <div className="text-mono-label text-[var(--color-on-surface-variant)] mt-1 text-xs">{role.id}</div>
                  </td>
                  <td className="px-6 py-4 text-body-md text-[var(--color-on-surface)]">{role.descripcion}</td>
                  <td className="px-6 py-4">
                    <span className="bg-[#ccfbf1] text-[#115e59] px-2 py-1 rounded-full text-xs font-bold">
                      {role.estado}
                    </span>
                  </td>
                  <td className="px-6 py-4 text-right space-x-2">
                    <button className="p-2 text-[var(--color-on-surface-variant)] hover:text-[var(--color-primary)] hover:bg-[var(--color-primary-container)] rounded transition-colors" title="Asignar permisos">
                      <Edit size={18} />
                    </button>
                    <button onClick={() => handleDelete(role.id)} className="p-2 text-[var(--color-on-surface-variant)] hover:text-[var(--color-error)] hover:bg-[var(--color-error-container)] rounded transition-colors" title="Eliminar">
                      <Trash2 size={18} />
                    </button>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      {isModalOpen && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg shadow-elevation-2 w-full max-w-md border border-[var(--color-outline-variant)]">
            <div className="px-6 py-4 border-b border-[var(--color-outline-variant)] flex justify-between items-center">
              <h2 className="text-headline-sm text-[var(--color-on-surface)]">Crear Nuevo Rol</h2>
              <button onClick={() => setIsModalOpen(false)} className="text-[var(--color-on-surface-variant)] hover:text-[var(--color-on-surface)]">
                &times;
              </button>
            </div>
            <form onSubmit={handleSubmit(onSubmit)} className="p-6 space-y-4">
              <div>
                <label className="block text-label-md text-[var(--color-on-surface)] mb-1">NOMBRE (MAYÚSCULAS)</label>
                <input
                  {...register('nombre')}
                  className={`w-full px-3 py-2 border rounded text-body-md focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)] ${errors.nombre ? 'border-[var(--color-error)]' : 'border-[var(--color-outline-variant)]'}`}
                  placeholder="EJ: SUPER_ADMIN"
                  onChange={(e) => e.target.value = e.target.value.toUpperCase()}
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
                <button
                  type="button"
                  onClick={() => setIsModalOpen(false)}
                  className="px-4 py-2 border border-[var(--color-outline-variant)] text-[var(--color-on-surface)] rounded hover:bg-[var(--color-surface-container-low)]"
                >
                  Cancelar
                </button>
                <button
                  type="submit"
                  disabled={isSubmitting}
                  className="px-4 py-2 bg-[var(--color-primary)] text-white rounded hover:bg-[#0f0f5c] disabled:opacity-50"
                >
                  {isSubmitting ? 'Guardando...' : 'Crear Rol'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
