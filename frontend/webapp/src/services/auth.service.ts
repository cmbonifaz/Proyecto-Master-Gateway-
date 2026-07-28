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

  /**
   * Validates the current JWT session via the internals endpoint.
   * The token is sent in the Authorization header by the apiAuth interceptor.
   * No token is sent in the body to avoid redundancy.
   */
  validateToken: async () => {
    const { data } = await apiAuth.post('/api/internals/validate-token', {});
    return data;
  },
};
