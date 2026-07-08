'use client';

import React, { useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { useAuth } from '@/context/AuthContext';
import { Lock } from 'lucide-react';

const loginSchema = z.object({
  email: z.string().email({ message: 'Correo electrónico inválido' }),
  password: z.string().min(8, { message: 'La contraseña debe tener al menos 8 caracteres' }),
});

type LoginFormValues = z.infer<typeof loginSchema>;

export default function LoginPage() {
  const { login, selectRole } = useAuth();
  const [step, setStep] = useState<1 | 2>(1);
  const [tempToken, setTempToken] = useState('');
  const [availableRoles, setAvailableRoles] = useState<any[]>([]);
  const [serverError, setServerError] = useState('');
  
  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<LoginFormValues>({
    resolver: zodResolver(loginSchema),
  });

  const onSubmit = async (data: LoginFormValues) => {
    setServerError('');
    try {
      const result = await login(data);
      setTempToken(result.temp_token);
      setAvailableRoles(result.roles);
      if (result.roles.length === 1) {
        // Auto select if only 1 role
        await selectRole(result.temp_token, result.roles[0].id);
      } else {
        setStep(2);
      }
    } catch (err: any) {
      setServerError(err.response?.data?.detail || 'Credenciales incorrectas o error en el servidor');
    }
  };

  const handleRoleSelect = async (roleId: string) => {
    try {
      await selectRole(tempToken, roleId);
    } catch (err: any) {
      setServerError(err.response?.data?.detail || 'Error seleccionando el rol');
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-[var(--color-background)]">
      <div className="bg-white p-8 rounded-lg shadow-elevation-2 border border-[var(--color-outline-variant)] w-full max-w-md">
        <div className="flex flex-col items-center mb-6">
          <div className="w-12 h-12 bg-[var(--color-primary-container)] text-[var(--color-on-primary-container)] rounded-full flex items-center justify-center mb-4">
            <Lock size={24} />
          </div>
          <h1 className="text-headline-md text-center text-[var(--color-primary)]">Master Gateway</h1>
          <p className="text-body-sm text-[var(--color-on-surface-variant)] mt-1">Acceso Seguro</p>
        </div>

        {serverError && (
          <div className="bg-[var(--color-error-container)] text-[var(--color-on-error-container)] p-3 rounded-md text-body-sm mb-4 border border-[#ffb4ab]">
            {serverError}
          </div>
        )}

        {step === 1 ? (
          <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
            <div>
              <label className="block text-label-md text-[var(--color-on-surface)] mb-1">CORREO ELECTRÓNICO</label>
              <input
                type="email"
                {...register('email')}
                className={`w-full px-3 py-2 border rounded text-body-md focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)] focus:border-transparent ${errors.email ? 'border-[var(--color-error)]' : 'border-[var(--color-outline-variant)]'}`}
                placeholder="admin@gateway.local"
              />
              {errors.email && <p className="text-[var(--color-error)] text-body-sm mt-1">{errors.email.message}</p>}
            </div>

            <div>
              <label className="block text-label-md text-[var(--color-on-surface)] mb-1">CONTRASEÑA</label>
              <input
                type="password"
                {...register('password')}
                className={`w-full px-3 py-2 border rounded text-body-md focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)] focus:border-transparent ${errors.password ? 'border-[var(--color-error)]' : 'border-[var(--color-outline-variant)]'}`}
                placeholder="••••••••"
              />
              {errors.password && <p className="text-[var(--color-error)] text-body-sm mt-1">{errors.password.message}</p>}
            </div>

            <button
              type="submit"
              disabled={isSubmitting}
              className="w-full bg-[var(--color-primary)] text-white py-2 px-4 rounded hover:bg-[#0f0f5c] transition-colors text-label-md disabled:opacity-50 mt-6"
            >
              {isSubmitting ? 'VERIFICANDO...' : 'INICIAR SESIÓN'}
            </button>
          </form>
        ) : (
          <div className="space-y-4">
            <p className="text-body-md text-center mb-4">Selecciona el rol con el que deseas ingresar:</p>
            {availableRoles.map((r) => (
              <button
                key={r.id}
                onClick={() => handleRoleSelect(r.id)}
                className="w-full text-left p-3 border border-[var(--color-outline-variant)] rounded hover:bg-[var(--color-surface-container-low)] transition-colors flex justify-between items-center"
              >
                <div>
                  <span className="block font-semibold text-body-md text-[var(--color-primary)]">{r.nombre}</span>
                  <span className="block text-body-sm text-[var(--color-on-surface-variant)]">{r.descripcion}</span>
                </div>
              </button>
            ))}
            <button
              onClick={() => setStep(1)}
              className="w-full mt-4 text-body-sm text-[var(--color-on-surface-variant)] underline text-center"
            >
              Volver
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
