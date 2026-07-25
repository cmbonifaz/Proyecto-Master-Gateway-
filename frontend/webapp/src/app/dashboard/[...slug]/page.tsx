'use client';

import React from 'react';
import { usePathname } from 'next/navigation';
import { Construction, ArrowLeft, ExternalLink, Home } from 'lucide-react';
import Link from 'next/link';

export default function DashboardCatchAll() {
  const pathname = usePathname();

  // Get the last segment as a readable page name
  const segments = pathname.split('/').filter(Boolean);
  const pageName = segments[segments.length - 1]?.replace(/-/g, ' ') || 'página';

  return (
    <div className="space-y-6">
      <Link
        href="/dashboard"
        className="inline-flex items-center gap-2 text-body-sm text-[var(--color-on-surface-variant)] hover:text-[var(--color-primary)] transition-colors"
      >
        <ArrowLeft size={16} /> Volver al inicio
      </Link>

      <div className="bg-white rounded-xl shadow-elevation-1 border border-[var(--color-outline-variant)] overflow-hidden">
        {/* Header */}
        <div className="p-8 border-b border-[var(--color-outline-variant)] bg-gradient-to-r from-[var(--color-secondary-container)] to-[var(--color-surface-container-low)]">
          <div className="flex items-center gap-4">
            <div className="w-14 h-14 bg-white text-[var(--color-secondary)] rounded-xl flex items-center justify-center shadow-sm">
              <Construction size={28} />
            </div>
            <div>
              <h1 className="text-headline-md text-[var(--color-on-surface)] font-bold capitalize">
                {pageName}
              </h1>
              <p className="text-body-md text-[var(--color-on-surface-variant)] mt-1 font-mono">
                {pathname}
              </p>
            </div>
          </div>
        </div>

        {/* Body */}
        <div className="p-8 text-center">
          <div className="w-20 h-20 bg-[var(--color-surface-container-low)] rounded-full flex items-center justify-center mx-auto mb-6">
            <Construction size={36} className="text-[var(--color-on-surface-variant)] opacity-40" />
          </div>
          <h2 className="text-title-lg text-[var(--color-on-surface)] font-semibold mb-3">
            Sección en construcción
          </h2>
          <p className="text-body-md text-[var(--color-on-surface-variant)] max-w-md mx-auto">
            Esta sección del menú aún no tiene contenido implementado en el Master Gateway.
            El menú de navegación lateral ya funciona correctamente — el microservicio o módulo
            correspondiente a esta ruta aún no ha sido desplegado.
          </p>
          <div className="mt-6 flex items-center justify-center gap-3 flex-wrap">
            <div className="inline-flex items-center gap-2 px-4 py-2 bg-[var(--color-surface-container-low)] rounded-lg">
              <ExternalLink size={14} className="text-[var(--color-on-surface-variant)]" />
              <code className="text-body-sm text-[var(--color-on-surface-variant)] font-mono">{pathname}</code>
            </div>
            <Link
              href="/dashboard"
              className="inline-flex items-center gap-2 px-4 py-2 bg-[var(--color-primary)] text-white rounded-lg text-body-sm hover:bg-[#0f0f5c] transition-colors"
            >
              <Home size={14} />
              Ir al inicio
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}
