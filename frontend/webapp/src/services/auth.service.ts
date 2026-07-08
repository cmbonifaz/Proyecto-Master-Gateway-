import { api, apiAuth } from '../lib/api';

export const AuthService = {
  login: async (credentials: { email: string; password: string }) => {
    const { data } = await api.post('/api/auth/login', credentials);
    return data; // { temp_token, roles: [...] }
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
    const { data } = await apiAuth.post('/api/internals/validate-token');
    return data;
  }
};
