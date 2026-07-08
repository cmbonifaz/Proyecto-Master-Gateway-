'use client';

import React, { createContext, useContext, useState, useEffect } from 'react';
import { AuthService } from '../services/auth.service';
import { useRouter } from 'next/navigation';

interface AuthContextType {
  isAuthenticated: boolean;
  roles: any[];
  currentRole: any;
  login: (credentials: any) => Promise<any>;
  selectRole: (tempToken: string, roleId: string) => Promise<void>;
  logout: () => Promise<void>;
  loading: boolean;
}

const AuthContext = createContext<AuthContextType>({} as AuthContextType);

export const AuthProvider = ({ children }: { children: React.ReactNode }) => {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [loading, setLoading] = useState(true);
  const [roles, setRoles] = useState<any[]>([]);
  const [currentRole, setCurrentRole] = useState<any>(null);
  const router = useRouter();

  useEffect(() => {
    const token = localStorage.getItem('access_token');
    const roleId = localStorage.getItem('role_id');
    
    if (token) {
      AuthService.validateToken()
        .then(() => {
          setIsAuthenticated(true);
          setCurrentRole(roleId);
        })
        .catch(() => {
          setIsAuthenticated(false);
          localStorage.removeItem('access_token');
          localStorage.removeItem('refresh_token');
          localStorage.removeItem('role_id');
        })
        .finally(() => setLoading(false));
    } else {
      setLoading(false);
    }
  }, []);

  const login = async (credentials: any) => {
    const data = await AuthService.login(credentials);
    setRoles(data.roles);
    return data;
  };

  const selectRole = async (tempToken: string, roleId: string) => {
    const data = await AuthService.selectRole({ temp_token: tempToken, role_id: roleId });
    localStorage.setItem('access_token', data.access_token);
    localStorage.setItem('refresh_token', data.refresh_token);
    localStorage.setItem('role_id', roleId);
    setIsAuthenticated(true);
    setCurrentRole(roleId);
    router.push('/dashboard');
  };

  const logout = async () => {
    try {
      const refreshToken = localStorage.getItem('refresh_token');
      if (refreshToken) {
        await AuthService.logout(refreshToken);
      }
    } catch (e) {
      console.error(e);
    } finally {
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
      localStorage.removeItem('role_id');
      setIsAuthenticated(false);
      setCurrentRole(null);
      router.push('/login');
    }
  };

  return (
    <AuthContext.Provider value={{ isAuthenticated, roles, currentRole, login, selectRole, logout, loading }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => useContext(AuthContext);
