'use client';

import React, { useEffect, useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { ModulesService, Module } from '@/services/modules.service';
import { Layers, Plus, Trash2, Edit } from 'lucide-react';
import { AuditDetails } from '@/components/ui/AuditDetails';

const moduleSchema = z.object({
  nombre: z.string().min(3, "Mínimo 3 caracteres"),
  descripcion: z.string().optional(),
});

type ModuleFormValues = z.infer<typeof moduleSchema>;

export default function ModulesPage() {
  const [modules, setModules] = useState<Module[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingModule, setEditingModule] = useState<Module | null>(null);

  const { register, handleSubmit, reset, setValue, formState: { errors, isSubmitting } } = useForm<ModuleFormValues>({
    resolver: zodResolver(moduleSchema),
  });

  const fetchModules = async () => {
    setLoading(true);
    try {
      const data = await ModulesService.getModules();
      setModules(data);
    } catch (e: any) {
      setError(e.response?.data?.detail || 'Error cargando módulos');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchModules(); }, []);

  const openNewModal = () => {
    setEditingModule(null);
    reset({ nombre: '', descripcion: '' });
    setIsModalOpen(true);
  };

  const openEditModal = (mod: Module) => {
    setEditingModule(mod);
    setValue('nombre', mod.nombre);
    setValue('descripcion', mod.descripcion || '');
    setIsModalOpen(true);
  };

  const onSubmit = async (data: ModuleFormValues) => {
    try {
      if (editingModule) {
        await ModulesService.updateModule(editingModule.id, data);
      } else {
        await ModulesService.createModule(data);
      }
      setIsModalOpen(false);
      reset();
      setEditingModule(null);
      fetchModules();
    } catch (e: any) {
      setError(e.response?.data?.detail || `Error ${editingModule ? 'actualizando' : 'creando'} módulo`);
    }
  };

  const handleDelete = async (id: string) => {
    if (!confirm('¿Estás seguro de eliminar este módulo?')) return;
    try {
      await ModulesService.deleteModule(id);
      fetchModules();
    } catch (e: any) {
      alert(e.response?.data?.detail || 'Error eliminando módulo');
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-headline-lg text-[var(--color-on-surface)] flex items-center gap-3">
          <Layers size={32} className="text-[var(--color-primary)]" />
          Gestión de Módulos
        </h1>
        <button
          onClick={openNewModal}
          className="bg-[var(--color-primary)] text-white px-4 py-2 rounded flex items-center gap-2 hover:bg-[#0f0f5c] transition-colors"
        >
          <Plus size={20} /> Nuevo Módulo
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
            ) : modules.length === 0 ? (
              <tr><td colSpan={4} className="px-6 py-8 text-center text-[var(--color-on-surface-variant)]">No se encontraron módulos</td></tr>
            ) : (
              modules.map(mod => (
                <tr key={mod.id} className="hover:bg-[var(--color-surface-container-lowest)] transition-colors">
                  <td className="px-6 py-4">
                    <div className="text-body-md font-semibold text-[var(--color-primary)]">{mod.nombre}</div>
                    <div className="text-xs text-[var(--color-on-surface-variant)] mt-1 font-mono">{mod.id}</div>
                  </td>
                  <td className="px-6 py-4 text-body-md text-[var(--color-on-surface)]">
                    {mod.descripcion || <span className="italic text-[var(--color-on-surface-variant)]">Sin descripción</span>}
                  </td>
                  <td className="px-6 py-4">
                    <span className="bg-[#ccfbf1] text-[#115e59] px-2 py-1 rounded-full text-xs font-bold">{mod.estado}</span>
                  </td>
                  <td className="px-6 py-4 text-right space-x-1">
                    <AuditDetails data={mod} title="Auditoría de Módulo" />
                    <button onClick={() => openEditModal(mod)} className="p-2 text-[var(--color-on-surface-variant)] hover:text-[var(--color-primary)] hover:bg-[var(--color-primary-container)] rounded transition-colors inline-flex items-center justify-center" title="Editar">
                      <Edit size={18} />
                    </button>
                    <button onClick={() => handleDelete(mod.id)} className="p-2 text-[var(--color-on-surface-variant)] hover:text-[var(--color-error)] hover:bg-[var(--color-error-container)] rounded transition-colors inline-flex items-center justify-center" title="Eliminar">
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
              <h2 className="text-headline-sm text-[var(--color-on-surface)]">{editingModule ? 'Editar Módulo' : 'Crear Nuevo Módulo'}</h2>
              <button onClick={() => { setIsModalOpen(false); setEditingModule(null); }} className="text-[var(--color-on-surface-variant)] hover:text-[var(--color-on-surface)]">&times;</button>
            </div>
            <form onSubmit={handleSubmit(onSubmit)} className="p-6 space-y-4">
              <div>
                <label className="block text-label-md text-[var(--color-on-surface)] mb-1">NOMBRE *</label>
                <input
                  {...register('nombre')}
                  className={`w-full px-3 py-2 border rounded text-body-md focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)] ${errors.nombre ? 'border-[var(--color-error)]' : 'border-[var(--color-outline-variant)]'}`}
                  placeholder="Ej: Ventas"
                />
                {errors.nombre && <p className="text-[var(--color-error)] text-body-sm mt-1">{errors.nombre.message}</p>}
              </div>
              <div>
                <label className="block text-label-md text-[var(--color-on-surface)] mb-1">DESCRIPCIÓN (OPCIONAL)</label>
                <textarea
                  {...register('descripcion')}
                  className="w-full px-3 py-2 border border-[var(--color-outline-variant)] rounded text-body-md focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]"
                  placeholder="Descripción del módulo"
                  rows={3}
                />
              </div>
              <div className="flex justify-end gap-3 mt-6">
                <button type="button" onClick={() => { setIsModalOpen(false); setEditingModule(null); }}
                  className="px-4 py-2 border border-[var(--color-outline-variant)] text-[var(--color-on-surface)] rounded hover:bg-[var(--color-surface-container-low)]">
                  Cancelar
                </button>
                <button type="submit" disabled={isSubmitting}
                  className="px-4 py-2 bg-[var(--color-primary)] text-white rounded hover:bg-[#0f0f5c] disabled:opacity-50">
                  {isSubmitting ? 'Guardando...' : (editingModule ? 'Guardar Cambios' : 'Crear Módulo')}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
