'use client';

import React from 'react';
import { useParams, usePathname } from 'next/navigation';
import { Construction, ArrowLeft, ExternalLink } from 'lucide-react';
import Link from 'next/link';

export default function ModuleSubPage() {
  const params = useParams();
  const pathname = usePathname();
  const moduleId = params.moduleId as string;

  // Extract the sub-path segments
  const slugs = params.slug as string[] || [];
  const subPath = slugs.join('/');

  return (
    <div className="space-y-6">
      <Link
        href={`/dashboard/module/${moduleId}`}
        className="inline-flex items-center gap-2 text-body-sm text-[var(--color-on-surface-variant)] hover:text-[var(--color-primary)] transition-colors"
      >
        <ArrowLeft size={16} /> Volver al módulo
      </Link>

      <div className="bg-white rounded-xl shadow-elevation-1 border border-[var(--color-outline-variant)] overflow-hidden">
        {/* Header */}
        <div className="p-8 border-b border-[var(--color-outline-variant)] bg-gradient-to-r from-[var(--color-primary-container)] to-[var(--color-surface-container-low)]">
          <div className="flex items-center gap-4">
            <div className="w-14 h-14 bg-white text-[var(--color-primary)] rounded-xl flex items-center justify-center shadow-sm">
              <Construction size={28} />
            </div>
            <div>
              <h1 className="text-headline-md text-[var(--color-on-surface)] font-bold capitalize">
                {slugs[slugs.length - 1]?.replace(/-/g, ' ') || 'Página del módulo'}
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
            <Construction size={36} className="text-[var(--color-on-surface-variant)] opacity-50" />
          </div>
          <h2 className="text-title-lg text-[var(--color-on-surface)] font-semibold mb-3">
            Sección en construcción
          </h2>
          <p className="text-body-md text-[var(--color-on-surface-variant)] max-w-md mx-auto mb-2">
            Esta sección del módulo aún no tiene contenido implementado. El menú de navegación lateral
            ya está funcionando correctamente — el microservicio correspondiente aún no ha sido desarrollado.
          </p>
          <div className="mt-4 inline-flex items-center gap-2 px-4 py-2 bg-[var(--color-surface-container-low)] rounded-lg">
            <ExternalLink size={14} className="text-[var(--color-on-surface-variant)]" />
            <code className="text-body-sm text-[var(--color-on-surface-variant)] font-mono">{pathname}</code>
          </div>
        </div>
      </div>
    </div>
  );
}
