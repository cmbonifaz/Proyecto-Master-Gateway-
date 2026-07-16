'use client';

import React, { useEffect, useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { MenusService, Menu } from '@/services/menus.service';
import { Menu as MenuIcon, Plus, Trash2, Edit, ChevronRight } from 'lucide-react';

const menuSchema = z.object({
  texto: z.string().min(2, "Mínimo 2 caracteres"),
  url: z.string().optional(),
  icono: z.string().optional(),
  orden: z.string().optional(),
  parent_id: z.string().optional(),
});

type MenuFormValues = z.infer<typeof menuSchema>;

// Build tree from flat list
function buildTree(items: Menu[]): (Menu & { children: Menu[] })[] {
  const map: Record<string, Menu & { children: Menu[] }> = {};
  const roots: (Menu & { children: Menu[] })[] = [];
  items.forEach(item => { map[item.id] = { ...item, children: [] }; });
  items.forEach(item => {
    if (item.parent_id && map[item.parent_id]) {
      map[item.parent_id].children.push(map[item.id]);
    } else {
      roots.push(map[item.id]);
    }
  });
  return roots;
}

function MenuRow({ menu, depth, onDelete, onEdit }: {
  menu: Menu & { children: Menu[] };
  depth: number;
  onDelete: (id: string) => void;
  onEdit: (menu: Menu) => void;
}) {
  return (
    <>
      <tr className="hover:bg-[var(--color-surface-container-lowest)] transition-colors">
        <td className="px-6 py-4">
          <div className="flex items-center gap-2" style={{ paddingLeft: `${depth * 20}px` }}>
            {depth > 0 && <ChevronRight size={14} className="text-[var(--color-on-surface-variant)] flex-shrink-0" />}
            <div>
              <div className="text-body-md font-semibold text-[var(--color-primary)]">{menu.texto}</div>
              <div className="text-xs text-[var(--color-on-surface-variant)] mt-0.5 font-mono">{menu.id}</div>
            </div>
          </div>
        </td>
        <td className="px-6 py-4 text-body-md text-[var(--color-on-surface)] font-mono">{menu.url || <span className="text-[var(--color-on-surface-variant)] italic">Sin ruta (contenedor)</span>}</td>
        <td className="px-6 py-4 text-body-sm text-[var(--color-on-surface-variant)]">
          {menu.orden && <span className="mr-2">Orden: {menu.orden}</span>}
          {menu.icono && <code className="bg-[var(--color-surface-container-low)] px-1 rounded text-xs">{menu.icono}</code>}
          {!menu.orden && !menu.icono && <span className="italic">N/A</span>}
        </td>
        <td className="px-6 py-4">
          <span className="bg-[#ccfbf1] text-[#115e59] px-2 py-1 rounded-full text-xs font-bold">{menu.estado}</span>
        </td>
        <td className="px-6 py-4 text-right space-x-1">
          <button onClick={() => onEdit(menu)} className="p-2 text-[var(--color-on-surface-variant)] hover:text-[var(--color-primary)] hover:bg-[var(--color-primary-container)] rounded transition-colors" title="Editar">
            <Edit size={16} />
          </button>
          <button onClick={() => onDelete(menu.id)} className="p-2 text-[var(--color-on-surface-variant)] hover:text-[var(--color-error)] hover:bg-[var(--color-error-container)] rounded transition-colors" title="Eliminar">
            <Trash2 size={16} />
          </button>
        </td>
      </tr>
      {menu.children.map(child => (
        <MenuRow key={child.id} menu={child as Menu & { children: Menu[] }} depth={depth + 1} onDelete={onDelete} onEdit={onEdit} />
      ))}
    </>
  );
}

export default function MenusPage() {
  const [menus, setMenus] = useState<Menu[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingMenu, setEditingMenu] = useState<Menu | null>(null);

  const { register, handleSubmit, reset, setValue, formState: { errors, isSubmitting } } = useForm<MenuFormValues>({
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

  useEffect(() => { fetchMenus(); }, []);

  const openNewModal = () => {
    setEditingMenu(null);
    reset({ texto: '', url: '', icono: '', orden: '', parent_id: '' });
    setIsModalOpen(true);
  };

  const openEditModal = (menu: Menu) => {
    setEditingMenu(menu);
    setValue('texto', menu.texto);
    setValue('url', menu.url || '');
    setValue('icono', menu.icono || '');
    setValue('orden', menu.orden || '');
    setValue('parent_id', menu.parent_id || '');
    setIsModalOpen(true);
  };

  const onSubmit = async (data: MenuFormValues) => {
    try {
      const payload = {
        texto: data.texto,
        url: data.url || undefined,
        icono: data.icono || undefined,
        orden: data.orden || undefined,
        parent_id: data.parent_id || undefined,
      };
      if (editingMenu) {
        await MenusService.updateMenu(editingMenu.id, payload);
      } else {
        await MenusService.createMenu(payload);
      }
      setIsModalOpen(false);
      reset();
      setEditingMenu(null);
      fetchMenus();
    } catch (e: any) {
      setError(e.response?.data?.detail || `Error ${editingMenu ? 'actualizando' : 'creando'} menú`);
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

  const tree = buildTree(menus);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-headline-lg text-[var(--color-on-surface)] flex items-center gap-3">
          <MenuIcon size={32} className="text-[var(--color-primary)]" />
          Gestión de Menús
          <span className="text-body-sm text-[var(--color-on-surface-variant)] font-normal bg-[var(--color-surface-container-low)] px-2 py-1 rounded ml-1">
            {menus.length} registros
          </span>
        </h1>
        <button
          onClick={openNewModal}
          className="bg-[var(--color-primary)] text-white px-4 py-2 rounded flex items-center gap-2 hover:bg-[#0f0f5c] transition-colors"
        >
          <Plus size={20} /> Nuevo Menú
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
              <th className="px-6 py-3 text-label-md text-[var(--color-on-surface-variant)] uppercase">Texto / Jerarquía</th>
              <th className="px-6 py-3 text-label-md text-[var(--color-on-surface-variant)] uppercase">URL / Ruta</th>
              <th className="px-6 py-3 text-label-md text-[var(--color-on-surface-variant)] uppercase">Orden / Ícono</th>
              <th className="px-6 py-3 text-label-md text-[var(--color-on-surface-variant)] uppercase">Estado</th>
              <th className="px-6 py-3 text-label-md text-[var(--color-on-surface-variant)] uppercase text-right">Acciones</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-[var(--color-outline-variant)]">
            {loading ? (
              <tr><td colSpan={5} className="px-6 py-8 text-center text-[var(--color-on-surface-variant)]">Cargando...</td></tr>
            ) : tree.length === 0 ? (
              <tr><td colSpan={5} className="px-6 py-8 text-center text-[var(--color-on-surface-variant)]">No se encontraron menús</td></tr>
            ) : (
              tree.map(menu => (
                <MenuRow key={menu.id} menu={menu} depth={0} onDelete={handleDelete} onEdit={openEditModal} />
              ))
            )}
          </tbody>
        </table>
      </div>

      {isModalOpen && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg shadow-elevation-2 w-full max-w-md border border-[var(--color-outline-variant)]">
            <div className="px-6 py-4 border-b border-[var(--color-outline-variant)] flex justify-between items-center">
              <h2 className="text-headline-sm text-[var(--color-on-surface)]">{editingMenu ? 'Editar Menú' : 'Crear Nuevo Menú'}</h2>
              <button onClick={() => { setIsModalOpen(false); setEditingMenu(null); }} className="text-[var(--color-on-surface-variant)] hover:text-[var(--color-on-surface)]">&times;</button>
            </div>
            <form onSubmit={handleSubmit(onSubmit)} className="p-6 space-y-4">
              <div>
                <label className="block text-label-md text-[var(--color-on-surface)] mb-1">TEXTO A MOSTRAR *</label>
                <input
                  {...register('texto')}
                  className={`w-full px-3 py-2 border rounded text-body-md focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)] ${errors.texto ? 'border-[var(--color-error)]' : 'border-[var(--color-outline-variant)]'}`}
                  placeholder="Ej: Gestión de Pagos"
                />
                {errors.texto && <p className="text-[var(--color-error)] text-body-sm mt-1">{errors.texto.message}</p>}
              </div>

              <div>
                <label className="block text-label-md text-[var(--color-on-surface)] mb-1">MENÚ PADRE (OPCIONAL)</label>
                <select
                  {...register('parent_id')}
                  className="w-full px-3 py-2 border border-[var(--color-outline-variant)] rounded text-body-md focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)] bg-white"
                >
                  <option value="">— Ninguno (menú raíz) —</option>
                  {menus
                    .filter(m => !editingMenu || m.id !== editingMenu.id)
                    .map(m => (
                      <option key={m.id} value={m.id}>{m.parent_id ? `  ↳ ${m.texto}` : m.texto}</option>
                    ))}
                </select>
              </div>

              <div>
                <label className="block text-label-md text-[var(--color-on-surface)] mb-1">URL / RUTA (OPCIONAL)</label>
                <input
                  {...register('url')}
                  className="w-full px-3 py-2 border border-[var(--color-outline-variant)] rounded text-body-md focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]"
                  placeholder="Ej: /dashboard/pagos"
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-label-md text-[var(--color-on-surface)] mb-1">ÍCONO (OPCIONAL)</label>
                  <input
                    {...register('icono')}
                    className="w-full px-3 py-2 border border-[var(--color-outline-variant)] rounded text-body-md focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]"
                    placeholder="Ej: Shield"
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
                <button type="button" onClick={() => { setIsModalOpen(false); setEditingMenu(null); }}
                  className="px-4 py-2 border border-[var(--color-outline-variant)] text-[var(--color-on-surface)] rounded hover:bg-[var(--color-surface-container-low)]">
                  Cancelar
                </button>
                <button type="submit" disabled={isSubmitting}
                  className="px-4 py-2 bg-[var(--color-primary)] text-white rounded hover:bg-[#0f0f5c] disabled:opacity-50">
                  {isSubmitting ? 'Guardando...' : (editingMenu ? 'Guardar Cambios' : 'Crear Menú')}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
