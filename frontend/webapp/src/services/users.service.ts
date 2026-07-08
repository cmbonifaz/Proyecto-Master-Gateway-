import { apiAuth } from '../lib/api';

export interface User {
  id: string;
  email: string;
  nombre: string;
  estado: string;
  roles: any[];
}

export const UsersService = {
  getUsers: async () => {
    const { data } = await apiAuth.get('/api/users/');
    return data;
  },

  createUser: async (payload: { email: string; password?: string; nombre: string }) => {
    const { data } = await apiAuth.post('/api/users/', payload);
    return data;
  },

  updateUser: async (id: string, payload: any) => {
    const { data } = await apiAuth.put(`/api/users/${id}`, payload);
    return data;
  },

  deleteUser: async (id: string) => {
    const { data } = await apiAuth.delete(`/api/users/${id}`);
    return data;
  }
};
