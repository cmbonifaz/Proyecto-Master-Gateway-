'use client';

import React, { useState } from 'react';
import { History, X, Clock, User, ShieldAlert } from 'lucide-react';

export interface AuditData {
  id: string;
  estado: string;
  fecha_creacion?: string | Date;
  fecha_actualizacion?: string | Date;
  creado_por?: string | null;
  actualizado_por?: string | null;
  [key: string]: any;
}

interface AuditDetailsProps {
  data: AuditData;
  title?: string;
}

export function AuditDetails({ data, title = 'Detalles de Auditoría' }: AuditDetailsProps) {
  const [isOpen, setIsOpen] = useState(false);

  const formatDate = (dateVal?: string | Date) => {
    if (!dateVal) return 'N/A';
    try {
      const date = new Date(dateVal);
      if (isNaN(date.getTime())) return 'N/A';
      return date.toLocaleString('es-ES', {
        day: '2-digit',
        month: '2-digit',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit',
      });
    } catch {
      return 'N/A';
    }
  };

  return (
    <>
      <button
        onClick={() => setIsOpen(true)}
        className="p-2 text-[var(--color-on-surface-variant)] hover:text-[var(--color-primary)] hover:bg-[var(--color-primary-container)] rounded transition-colors inline-flex items-center justify-center"
        title="Ver auditoría y trazabilidad"
        type="button"
      >
        <History size={16} />
      </button>

      {isOpen && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-[60]">
          <div className="bg-white rounded-lg shadow-elevation-2 w-full max-w-md border border-[var(--color-outline-variant)] overflow-hidden">
            {/* Header */}
            <div className="px-6 py-4 border-b border-[var(--color-outline-variant)] bg-[var(--color-surface-container-low)] flex justify-between items-center">
              <h3 className="text-title-md font-bold text-[var(--color-on-surface)] flex items-center gap-2">
                <History size={18} className="text-[var(--color-primary)]" />
                {title}
              </h3>
              <button
                onClick={() => setIsOpen(false)}
                className="text-[var(--color-on-surface-variant)] hover:text-[var(--color-on-surface)] text-xl font-bold"
                type="button"
              >
                <X size={18} />
              </button>
            </div>

            {/* Content */}
            <div className="p-6 space-y-4 text-left">
              <div>
                <span className="block text-xs font-bold text-[var(--color-on-surface-variant)] uppercase tracking-wider">ID del Registro</span>
                <span className="block text-body-md font-mono bg-[var(--color-surface-container-low)] px-2 py-1 rounded text-xs mt-1 select-all truncate">
                  {data.id}
                </span>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <span className="block text-xs font-bold text-[var(--color-on-surface-variant)] uppercase tracking-wider">Estado Global</span>
                  <span className="block mt-1">
                    <span className={`px-2 py-0.5 rounded-full text-xs font-bold ${
                      data.estado === 'ACTIVO' 
                        ? 'bg-[#ccfbf1] text-[#115e59]' 
                        : 'bg-[#fee2e2] text-[#991b1b]'
                    }`}>
                      {data.estado}
                    </span>
                  </span>
                </div>
                <div>
                  <span className="block text-xs font-bold text-[var(--color-on-surface-variant)] uppercase tracking-wider">Integridad</span>
                  <span className="text-xs text-green-700 flex items-center gap-1 mt-1 font-medium">
                    <Clock size={12} /> Firme / No Editable
                  </span>
                </div>
              </div>

              <div className="border-t border-[var(--color-outline-variant)] pt-4 space-y-3">
                <h4 className="text-xs font-bold text-[var(--color-primary)] uppercase tracking-wider flex items-center gap-1.5">
                  <User size={12} /> Creación y Origen
                </h4>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <span className="block text-[11px] text-[var(--color-on-surface-variant)] uppercase">Fecha Creación</span>
                    <span className="block text-body-sm text-[var(--color-on-surface)] font-medium mt-0.5">
                      {formatDate(data.fecha_creacion)}
                    </span>
                  </div>
                  <div>
                    <span className="block text-[11px] text-[var(--color-on-surface-variant)] uppercase">Creado Por (UUID)</span>
                    <span className="block text-body-sm text-[var(--color-on-surface)] font-mono text-[11px] truncate mt-0.5" title={data.creado_por || 'Auto-registro / Sistema'}>
                      {data.creado_por || 'Auto-registro'}
                    </span>
                  </div>
                </div>
              </div>

              <div className="border-t border-[var(--color-outline-variant)] pt-4 space-y-3">
                <h4 className="text-xs font-bold text-[var(--color-secondary)] uppercase tracking-wider flex items-center gap-1.5">
                  <Clock size={12} /> Última Modificación
                </h4>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <span className="block text-[11px] text-[var(--color-on-surface-variant)] uppercase">Último Cambio</span>
                    <span className="block text-body-sm text-[var(--color-on-surface)] font-medium mt-0.5">
                      {formatDate(data.fecha_actualizacion)}
                    </span>
                  </div>
                  <div>
                    <span className="block text-[11px] text-[var(--color-on-surface-variant)] uppercase">Modificado Por (UUID)</span>
                    <span className="block text-body-sm text-[var(--color-on-surface)] font-mono text-[11px] truncate mt-0.5" title={data.actualizado_por || 'N/A'}>
                      {data.actualizado_por || 'N/A'}
                    </span>
                  </div>
                </div>
              </div>

              <div className="mt-4 p-3 bg-[#fff7ed] text-[#c2410c] rounded-lg flex items-start gap-2 border border-[#fed7aa] text-[11px]">
                <ShieldAlert size={14} className="mt-0.5 flex-shrink-0" />
                <span>
                  Los datos de auditoría son capturados automáticamente a nivel de base de datos y no pueden ser alterados o borrados por ningún rol.
                </span>
              </div>
            </div>

            {/* Footer */}
            <div className="px-6 py-4 border-t border-[var(--color-outline-variant)] bg-[var(--color-surface-container-low)] flex justify-end">
              <button
                onClick={() => setIsOpen(false)}
                className="px-4 py-2 bg-[var(--color-primary)] text-white rounded text-body-sm hover:bg-[#0f0f5c] transition-colors"
                type="button"
              >
                Cerrar
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
}
