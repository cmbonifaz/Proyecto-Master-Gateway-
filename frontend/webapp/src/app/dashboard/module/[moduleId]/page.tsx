'use client';

import React, { useEffect, useState } from 'react';
import { useParams, usePathname } from 'next/navigation';
import { ModulesService, Module } from '@/services/modules.service';
import { MenusService } from '@/services/menus.service';
import { Layers, Loader2, ArrowLeft, Construction, ExternalLink } from 'lucide-react';
import Link from 'next/link';
import { ALL_ICONS } from '@/components/ui/IconPicker';

interface MenuNode {
  id: string;
  texto: string;
  url?: string | null;
  icono?: string | null;
  children: MenuNode[];
}

export default function ModuleDashboardPage() {
  const params = useParams();
  const pathname = usePathname();
  const moduleId = params.moduleId as string;
  const [moduleData, setModuleData] = useState<Module | null>(null);
  const [menuTree, setMenuTree] = useState<MenuNode[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(false);

  useEffect(() => {
    if (!moduleId) return;

    const fetchData = async () => {
      try {
        setLoading(true);
        const [data, tree] = await Promise.all([
          ModulesService.getModuleById(moduleId),
          MenusService.getMenuTree(),
        ]);
        setModuleData(data);
        // Filter to only this module's menus
        const modulMenus = tree.filter((n: MenuNode) => (n as any).modulo_id === moduleId);
        setMenuTree(modulMenus);
        setError(false);
      } catch (err) {
        console.error("Error fetching module:", err);
        setError(true);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [moduleId]);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-[60vh]">
        <Loader2 size={48} className="animate-spin text-[var(--color-primary)] opacity-50" />
      </div>
    );
  }

  if (error || !moduleData) {
    return (
      <div className="bg-[var(--color-error-container)] text-[var(--color-on-error-container)] p-6 rounded-lg border border-[#ffb4ab] mt-8">
        <h2 className="text-title-lg font-bold mb-2">Error</h2>
        <p className="text-body-md">No se pudo cargar la información del módulo. Es posible que no exista o no tengas permisos.</p>
        <Link href="/dashboard" className="inline-flex items-center gap-2 mt-4 text-[var(--color-primary)] font-semibold hover:underline">
          <ArrowLeft size={16} /> Volver al inicio
        </Link>
      </div>
    );
  }

  const moduleMenus = menuTree.filter((n: any) => n.modulo_id === moduleId);

  return (
    <div className="space-y-6">
      <Link href="/dashboard" className="inline-flex items-center gap-2 text-body-sm text-[var(--color-on-surface-variant)] hover:text-[var(--color-primary)] transition-colors mb-2">
        <ArrowLeft size={16} /> Volver a módulos
      </Link>

      {/* Module header card */}
      <div className="bg-white p-8 rounded-lg shadow-elevation-1 border border-[var(--color-outline-variant)]">
        <div className="flex items-center gap-4 mb-4">
          <div className="w-16 h-16 bg-[var(--color-primary-container)] text-[var(--color-on-primary-container)] rounded-xl flex items-center justify-center">
            <Layers size={32} />
          </div>
          <div>
            <h1 className="text-headline-lg text-[var(--color-on-surface)] font-bold">{moduleData.nombre}</h1>
            <p className="text-title-md text-[var(--color-primary)] mt-1">Panel Principal</p>
          </div>
        </div>

        {moduleData.descripcion && (
          <div className="mt-4 pt-4 border-t border-[var(--color-outline-variant)]">
            <p className="text-body-lg text-[var(--color-on-surface-variant)]">
              {moduleData.descripcion}
            </p>
          </div>
        )}
      </div>

      {/* Quick access cards for menu items */}
      {moduleMenus.length > 0 && (
        <div>
          <h2 className="text-title-lg text-[var(--color-on-surface)] font-bold mb-4">Acceso Rápido</h2>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {moduleMenus.map((item: MenuNode, idx) => {
              const IconCmp = item.icono ? (ALL_ICONS[item.icono] || Layers) : Layers;
              const colors = [
                { bg: 'bg-blue-50', text: 'text-blue-600', border: 'border-blue-100', hover: 'hover:border-blue-300' },
                { bg: 'bg-purple-50', text: 'text-purple-600', border: 'border-purple-100', hover: 'hover:border-purple-300' },
                { bg: 'bg-emerald-50', text: 'text-emerald-600', border: 'border-emerald-100', hover: 'hover:border-emerald-300' },
                { bg: 'bg-orange-50', text: 'text-orange-600', border: 'border-orange-100', hover: 'hover:border-orange-300' },
                { bg: 'bg-rose-50', text: 'text-rose-600', border: 'border-rose-100', hover: 'hover:border-rose-300' },
                { bg: 'bg-cyan-50', text: 'text-cyan-600', border: 'border-cyan-100', hover: 'hover:border-cyan-300' },
              ][idx % 6];

              if (item.url) {
                return (
                  <Link
                    key={item.id}
                    href={item.url}
                    className={`bg-white p-5 rounded-xl border-2 ${colors.border} ${colors.hover} shadow-sm hover:shadow-md transition-all flex items-center gap-4 group`}
                  >
                    <div className={`w-12 h-12 ${colors.bg} ${colors.text} rounded-lg flex items-center justify-center flex-shrink-0 group-hover:scale-110 transition-transform`}>
                      <IconCmp size={24} />
                    </div>
                    <div>
                      <p className={`text-body-md font-semibold ${colors.text}`}>{item.texto}</p>
                      <p className="text-body-sm text-[var(--color-on-surface-variant)] font-mono mt-0.5 truncate">{item.url}</p>
                    </div>
                  </Link>
                );
              }

              // Container menus (no URL) — show children
              return (
                <div key={item.id} className={`bg-white p-5 rounded-xl border-2 ${colors.border} shadow-sm`}>
                  <div className="flex items-center gap-3 mb-3">
                    <div className={`w-10 h-10 ${colors.bg} ${colors.text} rounded-lg flex items-center justify-center flex-shrink-0`}>
                      <IconCmp size={20} />
                    </div>
                    <p className="text-body-md font-semibold text-[var(--color-on-surface)]">{item.texto}</p>
                  </div>
                  {item.children.length > 0 && (
                    <div className="space-y-1 pl-2">
                      {item.children.map(child => {
                        const ChildIcon = child.icono ? (ALL_ICONS[child.icono] || ExternalLink) : ExternalLink;
                        return child.url ? (
                          <Link
                            key={child.id}
                            href={child.url}
                            className={`flex items-center gap-2 text-body-sm ${colors.text} hover:underline py-0.5`}
                          >
                            <ChildIcon size={14} />
                            {child.texto}
                          </Link>
                        ) : (
                          <span key={child.id} className="flex items-center gap-2 text-body-sm text-[var(--color-on-surface-variant)] py-0.5">
                            <ChildIcon size={14} />
                            {child.texto}
                          </span>
                        );
                      })}
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        </div>
      )}

      {moduleMenus.length === 0 && (
        <div className="mt-4 bg-[var(--color-surface-container-low)] p-6 rounded-lg border border-[var(--color-outline-variant)] text-center">
          <p className="text-body-md text-[var(--color-on-surface-variant)]">
            Usa el menú lateral para navegar por las opciones disponibles en este módulo.
          </p>
        </div>
      )}
    </div>
  );
}
