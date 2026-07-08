'use client';

import React, { useEffect, useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { UsersService, User } from '@/services/users.service';
import { Users, Plus, Trash2, Edit } from 'lucide-react';

const userSchema = z.object({
  email: z.string().email("Correo inválido"),
  nombre: z.string().min(2, "Mínimo 2 caracteres"),
  password: z.string().min(8, "Mínimo 8 caracteres").optional().or(z.literal('')),
});

type UserFormValues = z.infer<typeof userSchema>;

export default function UsersPage() {
  const [users, setUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingUserId, setEditingUserId] = useState<string | null>(null);

  const { register, handleSubmit, reset, setValue, formState: { errors, isSubmitting } } = useForm<UserFormValues>({
    resolver: zodResolver(userSchema),
  });

  const fetchUsers = async () => {
    setLoading(true);
    try {
      const data = await UsersService.getUsers();
      setUsers(data);
    } catch (e: any) {
      setError(e.response?.data?.detail || 'Error cargando usuarios');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchUsers();
  }, []);

  const openNewModal = () => {
    setEditingUserId(null);
    reset({ email: '', nombre: '', password: '' });
    setIsModalOpen(true);
  };

  const openEditModal = (user: User) => {
    setEditingUserId(user.id);
    setValue('email', user.email);
    setValue('nombre', user.nombre);
    setValue('password', ''); // No mostramos la password
    setIsModalOpen(true);
  };

  const onSubmit = async (data: UserFormValues) => {
    try {
      if (editingUserId) {
        const payload: any = { email: data.email, nombre: data.nombre };
        if (data.password) payload.password = data.password;
        await UsersService.updateUser(editingUserId, payload);
      } else {
        if (!data.password) {
          throw new Error('La contraseña es obligatoria para nuevos usuarios');
        }
        await UsersService.createUser({ email: data.email, nombre: data.nombre, password: data.password });
      }
      setIsModalOpen(false);
      reset();
      fetchUsers();
    } catch (e: any) {
      setError(e.message || e.response?.data?.detail || 'Error guardando usuario');
    }
  };

  const handleDelete = async (id: string) => {
    if (!confirm('¿Estás seguro de inactivar/eliminar este usuario?')) return;
    try {
      await UsersService.deleteUser(id);
      fetchUsers();
    } catch (e: any) {
      alert(e.response?.data?.detail || 'Error eliminando usuario');
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-headline-lg text-[var(--color-on-surface)] flex items-center gap-3">
          <Users size={32} className="text-[var(--color-primary)]" />
          Gestión de Usuarios
        </h1>
        <button
          onClick={openNewModal}
          className="bg-[var(--color-primary)] text-white px-4 py-2 rounded flex items-center gap-2 hover:bg-[#0f0f5c] transition-colors"
        >
          <Plus size={20} /> Nuevo Usuario
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
              <th className="px-6 py-3 text-label-md text-[var(--color-on-surface-variant)] uppercase">Email</th>
              <th className="px-6 py-3 text-label-md text-[var(--color-on-surface-variant)] uppercase">Estado</th>
              <th className="px-6 py-3 text-label-md text-[var(--color-on-surface-variant)] uppercase">Roles</th>
              <th className="px-6 py-3 text-label-md text-[var(--color-on-surface-variant)] uppercase text-right">Acciones</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-[var(--color-outline-variant)]">
            {loading ? (
              <tr>
                <td colSpan={5} className="px-6 py-8 text-center text-[var(--color-on-surface-variant)]">Cargando...</td>
              </tr>
            ) : users.length === 0 ? (
              <tr>
                <td colSpan={5} className="px-6 py-8 text-center text-[var(--color-on-surface-variant)]">No se encontraron usuarios</td>
              </tr>
            ) : (
              users.map(user => (
                <tr key={user.id} className="hover:bg-[var(--color-surface-container-lowest)] transition-colors">
                  <td className="px-6 py-4">
                    <div className="text-body-md font-semibold text-[var(--color-primary)]">{user.nombre}</div>
                    <div className="text-mono-label text-[var(--color-on-surface-variant)] mt-1 text-xs">{user.id}</div>
                  </td>
                  <td className="px-6 py-4 text-body-md text-[var(--color-on-surface)]">{user.email}</td>
                  <td className="px-6 py-4">
                    <span className={`px-2 py-1 rounded-full text-xs font-bold ${user.estado === 'ACTIVO' ? 'bg-[#ccfbf1] text-[#115e59]' : 'bg-[#fee2e2] text-[#991b1b]'}`}>
                      {user.estado}
                    </span>
                  </td>
                  <td className="px-6 py-4 text-body-sm text-[var(--color-on-surface-variant)]">
                    {user.roles?.map(r => r.nombre).join(', ') || 'Sin roles'}
                  </td>
                  <td className="px-6 py-4 text-right space-x-2">
                    <button onClick={() => openEditModal(user)} className="p-2 text-[var(--color-on-surface-variant)] hover:text-[var(--color-primary)] hover:bg-[var(--color-primary-container)] rounded transition-colors" title="Editar">
                      <Edit size={18} />
                    </button>
                    <button onClick={() => handleDelete(user.id)} className="p-2 text-[var(--color-on-surface-variant)] hover:text-[var(--color-error)] hover:bg-[var(--color-error-container)] rounded transition-colors" title="Eliminar/Inactivar">
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
              <h2 className="text-headline-sm text-[var(--color-on-surface)]">{editingUserId ? 'Editar Usuario' : 'Nuevo Usuario'}</h2>
              <button onClick={() => setIsModalOpen(false)} className="text-[var(--color-on-surface-variant)] hover:text-[var(--color-on-surface)]">
                &times;
              </button>
            </div>
            <form onSubmit={handleSubmit(onSubmit)} className="p-6 space-y-4">
              <div>
                <label className="block text-label-md text-[var(--color-on-surface)] mb-1">NOMBRE COMPLETO</label>
                <input
                  {...register('nombre')}
                  className={`w-full px-3 py-2 border rounded text-body-md focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)] ${errors.nombre ? 'border-[var(--color-error)]' : 'border-[var(--color-outline-variant)]'}`}
                  placeholder="Ej: Juan Pérez"
                />
                {errors.nombre && <p className="text-[var(--color-error)] text-body-sm mt-1">{errors.nombre.message}</p>}
              </div>

              <div>
                <label className="block text-label-md text-[var(--color-on-surface)] mb-1">CORREO ELECTRÓNICO</label>
                <input
                  type="email"
                  {...register('email')}
                  className={`w-full px-3 py-2 border rounded text-body-md focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)] ${errors.email ? 'border-[var(--color-error)]' : 'border-[var(--color-outline-variant)]'}`}
                  placeholder="juan@gateway.local"
                />
                {errors.email && <p className="text-[var(--color-error)] text-body-sm mt-1">{errors.email.message}</p>}
              </div>

              <div>
                <label className="block text-label-md text-[var(--color-on-surface)] mb-1">
                  CONTRASEÑA {editingUserId && '(DEJAR EN BLANCO PARA NO CAMBIAR)'}
                </label>
                <input
                  type="password"
                  {...register('password')}
                  className={`w-full px-3 py-2 border rounded text-body-md focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)] ${errors.password ? 'border-[var(--color-error)]' : 'border-[var(--color-outline-variant)]'}`}
                  placeholder="••••••••"
                />
                {errors.password && <p className="text-[var(--color-error)] text-body-sm mt-1">{errors.password.message}</p>}
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
                  {isSubmitting ? 'Guardando...' : 'Guardar Usuario'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
