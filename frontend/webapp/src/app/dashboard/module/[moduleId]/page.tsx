'use client';

import React, { useEffect, useState } from 'react';
import { useParams } from 'next/navigation';
import { ModulesService, Module } from '@/services/modules.service';
import { Layers, Loader2, ArrowLeft } from 'lucide-react';
import Link from 'next/link';

export default function ModuleDashboardPage() {
  const params = useParams();
  const moduleId = params.moduleId as string;
  const [moduleData, setModuleData] = useState<Module | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(false);

  useEffect(() => {
    if (!moduleId) return;
    
    const fetchModule = async () => {
      try {
        setLoading(true);
        const data = await ModulesService.getModuleById(moduleId);
        setModuleData(data);
        setError(false);
      } catch (err) {
        console.error("Error fetching module:", err);
        setError(true);
      } finally {
        setLoading(false);
      }
    };

    fetchModule();
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

  return (
    <div className="space-y-6">
      <Link href="/dashboard" className="inline-flex items-center gap-2 text-body-sm text-[var(--color-on-surface-variant)] hover:text-[var(--color-primary)] transition-colors mb-2">
        <ArrowLeft size={16} /> Volver a módulos
      </Link>
      
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
        
        <div className="mt-6 pt-6 border-t border-[var(--color-outline-variant)]">
          <p className="text-body-lg text-[var(--color-on-surface-variant)]">
            {moduleData.descripcion || 'Este módulo no tiene una descripción detallada.'}
          </p>
        </div>
      </div>

      <div className="mt-8 bg-[var(--color-surface-container-low)] p-6 rounded-lg border border-[var(--color-outline-variant)] text-center">
        <p className="text-body-md text-[var(--color-on-surface-variant)]">
          Usa el menú lateral para navegar por las opciones disponibles en este módulo.
        </p>
      </div>
    </div>
  );
}
