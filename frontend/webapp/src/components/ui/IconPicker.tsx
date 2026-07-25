'use client';

import React, { useState } from 'react';
import {
  Shield, Users, Layers, Menu as MenuIcon, LayoutDashboard,
  Activity, Server, Box, Settings, User, FileText, Database, CreditCard,
  Briefcase, Calendar, Folder, Home, ShoppingCart, Package, BarChart2,
  UserCheck, Bell, Truck, Car, Wrench, MapPin, ClipboardList, DollarSign,
  PieChart, TrendingUp, Lock, Key, Globe, Mail, Phone, Star, Heart,
  AlertTriangle, CheckCircle, Clock, Archive, Tag, Search, Filter,
  Download, Upload, Printer, Eye, Edit, Trash2, Plus, Minus,
  ChevronRight, ChevronDown, ExternalLink, Link as LinkIcon,
} from 'lucide-react';

export const ALL_ICONS: Record<string, React.ElementType> = {
  Shield, Users, Layers, Menu: MenuIcon, LayoutDashboard,
  Activity, Server, Box, Settings, User, FileText, Database, CreditCard,
  Briefcase, Calendar, Folder, Home, ShoppingCart, Package, BarChart2,
  UserCheck, Bell, Truck, Car, Wrench, MapPin, ClipboardList, DollarSign,
  PieChart, TrendingUp, Lock, Key, Globe, Mail, Phone, Star, Heart,
  AlertTriangle, CheckCircle, Clock, Archive, Tag, Search, Filter,
  Download, Upload, Printer, Eye, Edit, Trash2, Plus, Minus,
  ChevronRight, ChevronDown, ExternalLink, Link: LinkIcon,
};

export const ICON_NAMES = Object.keys(ALL_ICONS);

interface IconPickerProps {
  value: string;
  onChange: (iconName: string) => void;
}

export function IconPicker({ value, onChange }: IconPickerProps) {
  const [open, setOpen] = useState(false);
  const [search, setSearch] = useState('');

  const filtered = ICON_NAMES.filter(name =>
    name.toLowerCase().includes(search.toLowerCase())
  );

  const SelectedIcon = value ? (ALL_ICONS[value] || null) : null;

  return (
    <div className="relative">
      {/* Trigger button */}
      <button
        type="button"
        onClick={() => setOpen(v => !v)}
        className="w-full flex items-center gap-3 px-3 py-2 border border-[var(--color-outline-variant)] rounded text-body-md focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)] bg-white hover:bg-[var(--color-surface-container-low)] transition-colors"
      >
        <div className="w-7 h-7 bg-[var(--color-primary-container)] text-[var(--color-on-primary-container)] rounded flex items-center justify-center flex-shrink-0">
          {SelectedIcon ? <SelectedIcon size={16} /> : <Box size={16} className="opacity-40" />}
        </div>
        <span className="flex-1 text-left text-body-md text-[var(--color-on-surface)]">
          {value || <span className="text-[var(--color-on-surface-variant)] italic">Seleccionar ícono...</span>}
        </span>
        <ChevronDown size={14} className={`opacity-60 transition-transform ${open ? 'rotate-180' : ''}`} />
      </button>

      {/* Dropdown panel */}
      {open && (
        <>
          {/* Backdrop */}
          <div className="fixed inset-0 z-10" onClick={() => setOpen(false)} />
          <div className="absolute z-20 mt-1 left-0 right-0 bg-white border border-[var(--color-outline-variant)] rounded-lg shadow-elevation-3 overflow-hidden">
            {/* Search */}
            <div className="p-2 border-b border-[var(--color-outline-variant)]">
              <div className="relative">
                <Search size={14} className="absolute left-2.5 top-1/2 -translate-y-1/2 text-[var(--color-on-surface-variant)]" />
                <input
                  type="text"
                  value={search}
                  onChange={e => setSearch(e.target.value)}
                  placeholder="Buscar ícono..."
                  className="w-full pl-8 pr-3 py-1.5 text-body-sm border border-[var(--color-outline-variant)] rounded focus:outline-none focus:ring-1 focus:ring-[var(--color-primary)]"
                  autoFocus
                />
              </div>
            </div>
            {/* None option */}
            <div className="px-2 pt-2">
              <button
                type="button"
                onClick={() => { onChange(''); setOpen(false); setSearch(''); }}
                className={`w-full flex items-center gap-2 px-2 py-1.5 rounded text-body-sm transition-colors mb-1 ${
                  !value ? 'bg-[var(--color-primary-container)] text-[var(--color-on-primary-container)]' : 'hover:bg-[var(--color-surface-container-low)] text-[var(--color-on-surface-variant)] italic'
                }`}
              >
                <div className="w-6 h-6 rounded bg-[var(--color-surface-container-low)] flex items-center justify-center opacity-40">
                  <Box size={14} />
                </div>
                Sin ícono
              </button>
            </div>
            {/* Grid of icons */}
            <div className="p-2 grid grid-cols-5 gap-1 max-h-48 overflow-y-auto">
              {filtered.map(name => {
                const IconCmp = ALL_ICONS[name];
                const isSelected = value === name;
                return (
                  <button
                    key={name}
                    type="button"
                    title={name}
                    onClick={() => { onChange(name); setOpen(false); setSearch(''); }}
                    className={`flex flex-col items-center justify-center gap-1 p-2 rounded-lg text-[10px] transition-all ${
                      isSelected
                        ? 'bg-[var(--color-primary)] text-white'
                        : 'hover:bg-[var(--color-surface-container-low)] text-[var(--color-on-surface-variant)]'
                    }`}
                  >
                    <IconCmp size={18} />
                    <span className="truncate w-full text-center leading-tight">{name}</span>
                  </button>
                );
              })}
              {filtered.length === 0 && (
                <div className="col-span-5 text-center py-4 text-body-sm text-[var(--color-on-surface-variant)] italic">
                  No se encontraron íconos
                </div>
              )}
            </div>
          </div>
        </>
      )}
    </div>
  );
}
