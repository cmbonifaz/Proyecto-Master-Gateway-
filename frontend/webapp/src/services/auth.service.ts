import { api, apiAuth } from '../lib/api';

export const AuthService = {
  login: async (credentials: { email: string; password: string }) => {
    const { data } = await api.post('/api/auth/login', credentials);
    return data; // { temp_token, roles: [...] }
  },

  register: async (credentials: { email: string; password: string; nombre: string }) => {
    const { data } = await api.post('/api/auth/register', credentials);
    return data;
  },

  selectRole: async (payload: { temp_token: string; role_id: string }) => {
    const { data } = await api.post('/api/auth/select-role', payload);
    return data; // { access_token, refresh_token, token_type }
  },

  logout: async (refreshToken: string) => {
    const { data } = await apiAuth.post('/api/auth/logout', { refresh_token: refreshToken });
    return data;
  },

  validateToken: async () => {
    const token = localStorage.getItem('access_token');
    const { data } = await apiAuth.post('/api/internals/validate-token', { token });
    return data;
  }
};
