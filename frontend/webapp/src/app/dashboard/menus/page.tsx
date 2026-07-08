'use client';

import React, { useEffect, useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { MenusService, Menu } from '@/services/menus.service';
import { Menu as MenuIcon, Plus, Trash2 } from 'lucide-react';

const menuSchema = z.object({
  texto: z.string().min(2, "Mínimo 2 caracteres"),
  url: z.string().optional(),
  icono: z.string().optional(),
  orden: z.string().optional(),
});

type MenuFormValues = z.infer<typeof menuSchema>;

export default function MenusPage() {
  const [menus, setMenus] = useState<Menu[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [isModalOpen, setIsModalOpen] = useState(false);

  const { register, handleSubmit, reset, formState: { errors, isSubmitting } } = useForm<MenuFormValues>({
    resolver: zodResolver(menuSchema),
  });

  const fetchMenus = async () => {
    setLoading(true);
    try {
      const data = await MenusService.getMenus();
      setMenus(data);
    } catch (e: any) {
      setError(e.response?.data?.detail || 'Error cargando menús');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchMenus();
  }, []);

  const onSubmit = async (data: MenuFormValues) => {
    try {
      await MenusService.createMenu(data);
      setIsModalOpen(false);
      reset();
      fetchMenus();
    } catch (e: any) {
      setError(e.response?.data?.detail || 'Error creando menú');
    }
  };

  const handleDelete = async (id: string) => {
    if (!confirm('¿Estás seguro de eliminar este menú?')) return;
    try {
      await MenusService.deleteMenu(id);
      fetchMenus();
    } catch (e: any) {
      alert(e.response?.data?.detail || 'Error eliminando menú');
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-headline-lg text-[var(--color-on-surface)] flex items-center gap-3">
          <MenuIcon size={32} className="text-[var(--color-primary)]" />
          Gestión de Menús
        </h1>
        <button
          onClick={() => setIsModalOpen(true)}
          className="bg-[var(--color-primary)] text-white px-4 py-2 rounded flex items-center gap-2 hover:bg-[#0f0f5c] transition-colors"
        >
          <Plus size={20} /> Nuevo Menú
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
              <th className="px-6 py-3 text-label-md text-[var(--color-on-surface-variant)] uppercase">Texto</th>
              <th className="px-6 py-3 text-label-md text-[var(--color-on-surface-variant)] uppercase">Ruta (URL)</th>
              <th className="px-6 py-3 text-label-md text-[var(--color-on-surface-variant)] uppercase">Orden / Ícono</th>
              <th className="px-6 py-3 text-label-md text-[var(--color-on-surface-variant)] uppercase">Estado</th>
              <th className="px-6 py-3 text-label-md text-[var(--color-on-surface-variant)] uppercase text-right">Acciones</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-[var(--color-outline-variant)]">
            {loading ? (
              <tr>
                <td colSpan={5} className="px-6 py-8 text-center text-[var(--color-on-surface-variant)]">Cargando...</td>
              </tr>
            ) : menus.length === 0 ? (
              <tr>
                <td colSpan={5} className="px-6 py-8 text-center text-[var(--color-on-surface-variant)]">No se encontraron menús</td>
              </tr>
            ) : (
              menus.map(menu => (
                <tr key={menu.id} className="hover:bg-[var(--color-surface-container-lowest)] transition-colors">
                  <td className="px-6 py-4">
                    <div className="text-body-md font-semibold text-[var(--color-primary)]">{menu.texto}</div>
                    <div className="text-mono-label text-[var(--color-on-surface-variant)] mt-1 text-xs">{menu.id}</div>
                  </td>
                  <td className="px-6 py-4 text-body-md text-[var(--color-on-surface)] font-mono">{menu.url || '-'}</td>
                  <td className="px-6 py-4 text-body-md text-[var(--color-on-surface-variant)]">
                    Orden: {menu.orden || 'N/A'}<br/>
                    Ícono: {menu.icono || 'N/A'}
                  </td>
                  <td className="px-6 py-4">
                    <span className="bg-[#ccfbf1] text-[#115e59] px-2 py-1 rounded-full text-xs font-bold">
                      {menu.estado}
                    </span>
                  </td>
                  <td className="px-6 py-4 text-right space-x-2">
                    <button onClick={() => handleDelete(menu.id)} className="p-2 text-[var(--color-on-surface-variant)] hover:text-[var(--color-error)] hover:bg-[var(--color-error-container)] rounded transition-colors" title="Eliminar">
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
              <h2 className="text-headline-sm text-[var(--color-on-surface)]">Crear Nuevo Menú</h2>
              <button onClick={() => setIsModalOpen(false)} className="text-[var(--color-on-surface-variant)] hover:text-[var(--color-on-surface)]">
                &times;
              </button>
            </div>
            <form onSubmit={handleSubmit(onSubmit)} className="p-6 space-y-4">
              <div>
                <label className="block text-label-md text-[var(--color-on-surface)] mb-1">TEXTO A MOSTRAR</label>
                <input
                  {...register('texto')}
                  className={`w-full px-3 py-2 border rounded text-body-md focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)] ${errors.texto ? 'border-[var(--color-error)]' : 'border-[var(--color-outline-variant)]'}`}
                  placeholder="Ej: Gestión de Pagos"
                />
                {errors.texto && <p className="text-[var(--color-error)] text-body-sm mt-1">{errors.texto.message}</p>}
              </div>

              <div>
                <label className="block text-label-md text-[var(--color-on-surface)] mb-1">URL / RUTA (OPCIONAL)</label>
                <input
                  {...register('url')}
                  className="w-full px-3 py-2 border border-[var(--color-outline-variant)] rounded text-body-md focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]"
                  placeholder="Ej: /pagos"
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-label-md text-[var(--color-on-surface)] mb-1">ÍCONO (OPCIONAL)</label>
                  <input
                    {...register('icono')}
                    className="w-full px-3 py-2 border border-[var(--color-outline-variant)] rounded text-body-md focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]"
                    placeholder="fas fa-icon"
                  />
                </div>
                <div>
                  <label className="block text-label-md text-[var(--color-on-surface)] mb-1">ORDEN (OPCIONAL)</label>
                  <input
                    {...register('orden')}
                    className="w-full px-3 py-2 border border-[var(--color-outline-variant)] rounded text-body-md focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]"
                    placeholder="Ej: 001"
                  />
                </div>
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
                  {isSubmitting ? 'Guardando...' : 'Crear Menú'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
