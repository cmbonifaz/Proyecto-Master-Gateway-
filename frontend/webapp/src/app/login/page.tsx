'use client';

import React, { useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { useAuth } from '@/context/AuthContext';
import { Lock, Check, X } from 'lucide-react';
import { AuthService } from '@/services/auth.service';

const loginSchema = z.object({
  email: z.string().email({ message: 'Correo electrónico inválido' }),
  password: z.string().min(8, { message: 'La contraseña debe tener al menos 8 caracteres' }),
});

const registerSchema = z.object({
  nombre: z.string().min(2, { message: 'El nombre es obligatorio' }),
  email: z.string().email({ message: 'Correo electrónico inválido' }),
  password: z.string().min(8, { message: 'La contraseña debe tener al menos 8 caracteres' }),
  confirmPassword: z.string()
}).refine((data) => data.password === data.confirmPassword, {
  message: "Las contraseñas no coinciden",
  path: ["confirmPassword"]
});

type LoginFormValues = z.infer<typeof loginSchema>;
type RegisterFormValues = z.infer<typeof registerSchema>;

export default function LoginPage() {
  const { login, selectRole } = useAuth();
  const [step, setStep] = useState<1 | 2>(1);
  const [isRegistering, setIsRegistering] = useState(false);
  const [tempToken, setTempToken] = useState('');
  const [availableRoles, setAvailableRoles] = useState<any[]>([]);
  const [serverError, setServerError] = useState('');
  const [successMessage, setSuccessMessage] = useState('');
  
  const {
    register: registerLogin,
    handleSubmit: handleLoginSubmit,
    formState: { errors: loginErrors, isSubmitting: isLoginSubmitting },
    reset: resetLogin
  } = useForm<LoginFormValues>({
    resolver: zodResolver(loginSchema),
  });

  const {
    register: registerForm,
    handleSubmit: handleRegisterSubmit,
    formState: { errors: registerErrors, isSubmitting: isRegisterSubmitting },
    reset: resetRegister,
    watch: watchRegister
  } = useForm<RegisterFormValues>({
    resolver: zodResolver(registerSchema),
  });

  const registerPassword = watchRegister ? watchRegister('password', '') : '';

  const passwordRequirements = [
    { label: 'Mínimo 8 caracteres', met: registerPassword.length >= 8 },
    { label: 'Al menos una mayúscula', met: /[A-Z]/.test(registerPassword) },
    { label: 'Al menos una minúscula', met: /[a-z]/.test(registerPassword) },
    { label: 'Al menos un número', met: /[0-9]/.test(registerPassword) },
    { label: 'Al menos un carácter especial (!@#$%^&...)', met: /[!@#$%^&*(),.?":{}|<>]/.test(registerPassword) },
  ];

  const handleAxiosError = (err: any, defaultMsg: string) => {
    const detail = err.response?.data?.detail;
    if (typeof detail === 'string') {
      return detail;
    }
    if (Array.isArray(detail)) {
      return detail.map((d: any) => d.msg ? d.msg.replace(/^Value error, /, '') : JSON.stringify(d)).join(', ');
    }
    if (detail && typeof detail === 'object') {
      return JSON.stringify(detail);
    }
    return defaultMsg;
  };

  const onLoginSubmit = async (data: LoginFormValues) => {
    setServerError('');
    setSuccessMessage('');
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
      setServerError(handleAxiosError(err, 'Credenciales incorrectas o error en el servidor'));
    }
  };

  const onRegisterSubmit = async (data: RegisterFormValues) => {
    setServerError('');
    setSuccessMessage('');
    try {
      await AuthService.register({
        nombre: data.nombre,
        email: data.email,
        password: data.password
      });
      setSuccessMessage('Registro exitoso. Espera a que un administrador te asigne un rol.');
      setIsRegistering(false);
      resetRegister();
    } catch (err: any) {
      setServerError(handleAxiosError(err, 'Error en el registro'));
    }
  };

  const handleRoleSelect = async (roleId: string) => {
    try {
      await selectRole(tempToken, roleId);
    } catch (err: any) {
      setServerError(handleAxiosError(err, 'Error seleccionando el rol'));
    }
  };

  const toggleMode = () => {
    setIsRegistering(!isRegistering);
    setServerError('');
    setSuccessMessage('');
    resetLogin();
    resetRegister();
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-[var(--color-background)]">
      <div className="bg-white p-8 rounded-lg shadow-elevation-2 border border-[var(--color-outline-variant)] w-full max-w-md my-8">
        <div className="flex flex-col items-center mb-6">
          <div className="w-12 h-12 bg-[var(--color-primary-container)] text-[var(--color-on-primary-container)] rounded-full flex items-center justify-center mb-4">
            <Lock size={24} />
          </div>
          <h1 className="text-headline-md text-center text-[var(--color-primary)]">Master Gateway</h1>
          <p className="text-body-sm text-[var(--color-on-surface-variant)] mt-1">
            {isRegistering ? 'Crear una cuenta' : 'Acceso Seguro'}
          </p>
        </div>

        {serverError && (
          <div className="bg-[var(--color-error-container)] text-[var(--color-on-error-container)] p-3 rounded-md text-body-sm mb-4 border border-[#ffb4ab]">
            {serverError}
          </div>
        )}

        {successMessage && (
          <div className="bg-[#d3ebd3] text-[#0f5132] p-3 rounded-md text-body-sm mb-4 border border-[#badbcc]">
            {successMessage}
          </div>
        )}

        {isRegistering ? (
          <form onSubmit={handleRegisterSubmit(onRegisterSubmit)} className="space-y-4">
            <div>
              <label className="block text-label-md text-[var(--color-on-surface)] mb-1">NOMBRE COMPLETO</label>
              <input
                type="text"
                {...registerForm('nombre')}
                className={`w-full px-3 py-2 border rounded text-body-md focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)] focus:border-transparent ${registerErrors.nombre ? 'border-[var(--color-error)]' : 'border-[var(--color-outline-variant)]'}`}
                placeholder="Juan Pérez"
              />
              {registerErrors.nombre && <p className="text-[var(--color-error)] text-body-sm mt-1">{registerErrors.nombre.message}</p>}
            </div>

            <div>
              <label className="block text-label-md text-[var(--color-on-surface)] mb-1">CORREO ELECTRÓNICO</label>
              <input
                type="email"
                {...registerForm('email')}
                className={`w-full px-3 py-2 border rounded text-body-md focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)] focus:border-transparent ${registerErrors.email ? 'border-[var(--color-error)]' : 'border-[var(--color-outline-variant)]'}`}
                placeholder="ejemplo@gateway.local"
              />
              {registerErrors.email && <p className="text-[var(--color-error)] text-body-sm mt-1">{registerErrors.email.message}</p>}
            </div>

            <div>
              <label className="block text-label-md text-[var(--color-on-surface)] mb-1">CONTRASEÑA</label>
              <input
                type="password"
                {...registerForm('password')}
                className={`w-full px-3 py-2 border rounded text-body-md focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)] focus:border-transparent ${registerErrors.password ? 'border-[var(--color-error)]' : 'border-[var(--color-outline-variant)]'}`}
                placeholder="••••••••"
              />
              {registerErrors.password && <p className="text-[var(--color-error)] text-body-sm mt-1">{registerErrors.password.message}</p>}
              
              {/* Feedback visual de requerimientos */}
              {registerPassword && (
                <div className="mt-2 space-y-1.5 bg-[var(--color-surface-container-low)] p-3 rounded-md border border-[var(--color-outline-variant)]">
                  <p className="text-[11px] font-semibold text-[var(--color-on-surface-variant)] uppercase tracking-wider mb-1">Criterios de Seguridad:</p>
                  {passwordRequirements.map((req, i) => (
                    <div key={i} className="flex items-center gap-2 text-body-sm transition-all duration-200">
                      {req.met ? (
                        <Check size={14} className="text-green-500 stroke-[3]" />
                      ) : (
                        <X size={14} className="text-[var(--color-outline)] opacity-50" />
                      )}
                      <span className={req.met ? 'text-green-800 font-medium' : 'text-[var(--color-on-surface-variant)] opacity-70'}>
                        {req.label}
                      </span>
                    </div>
                  ))}
                </div>
              )}
            </div>
            
            <div>
              <label className="block text-label-md text-[var(--color-on-surface)] mb-1">CONFIRMAR CONTRASEÑA</label>
              <input
                type="password"
                {...registerForm('confirmPassword')}
                className={`w-full px-3 py-2 border rounded text-body-md focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)] focus:border-transparent ${registerErrors.confirmPassword ? 'border-[var(--color-error)]' : 'border-[var(--color-outline-variant)]'}`}
                placeholder="••••••••"
              />
              {registerErrors.confirmPassword && <p className="text-[var(--color-error)] text-body-sm mt-1">{registerErrors.confirmPassword.message}</p>}
            </div>

            <button
              type="submit"
              disabled={isRegisterSubmitting}
              className="w-full bg-[var(--color-primary)] text-white py-2 px-4 rounded hover:bg-[#0f0f5c] transition-colors text-label-md disabled:opacity-50 mt-6"
            >
              {isRegisterSubmitting ? 'REGISTRANDO...' : 'REGISTRARSE'}
            </button>
            
            <p className="text-center text-body-sm mt-4">
              ¿Ya tienes cuenta?{' '}
              <button type="button" onClick={toggleMode} className="text-[var(--color-primary)] hover:underline">
                Inicia sesión aquí
              </button>
            </p>
          </form>
        ) : step === 1 ? (
          <form onSubmit={handleLoginSubmit(onLoginSubmit)} className="space-y-4">
            <div>
              <label className="block text-label-md text-[var(--color-on-surface)] mb-1">CORREO ELECTRÓNICO</label>
              <input
                type="email"
                {...registerLogin('email')}
                className={`w-full px-3 py-2 border rounded text-body-md focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)] focus:border-transparent ${loginErrors.email ? 'border-[var(--color-error)]' : 'border-[var(--color-outline-variant)]'}`}
                placeholder="admin@gateway.local"
              />
              {loginErrors.email && <p className="text-[var(--color-error)] text-body-sm mt-1">{loginErrors.email.message}</p>}
            </div>

            <div>
              <label className="block text-label-md text-[var(--color-on-surface)] mb-1">CONTRASEÑA</label>
              <input
                type="password"
                {...registerLogin('password')}
                className={`w-full px-3 py-2 border rounded text-body-md focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)] focus:border-transparent ${loginErrors.password ? 'border-[var(--color-error)]' : 'border-[var(--color-outline-variant)]'}`}
                placeholder="••••••••"
              />
              {loginErrors.password && <p className="text-[var(--color-error)] text-body-sm mt-1">{loginErrors.password.message}</p>}
            </div>

            <button
              type="submit"
              disabled={isLoginSubmitting}
              className="w-full bg-[var(--color-primary)] text-white py-2 px-4 rounded hover:bg-[#0f0f5c] transition-colors text-label-md disabled:opacity-50 mt-6"
            >
              {isLoginSubmitting ? 'VERIFICANDO...' : 'INICIAR SESIÓN'}
            </button>
            
            <p className="text-center text-body-sm mt-4">
              ¿No tienes cuenta?{' '}
              <button type="button" onClick={toggleMode} className="text-[var(--color-primary)] hover:underline">
                Regístrate aquí
              </button>
            </p>
          </form>
        ) : (
          <div className="space-y-4">
            <p className="text-body-md text-center mb-4">Selecciona el rol con el que deseas ingresar:</p>
            {availableRoles.length === 0 ? (
               <div className="text-center text-[var(--color-error)] text-body-sm my-4">
                  No tienes roles asignados. Un administrador debe asignarte un rol.
               </div>
            ) : availableRoles.map((r) => (
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
