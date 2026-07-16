import { apiAuth } from '../lib/api';

export interface Module {
  id: string;
  nombre: string;
  descripcion: string;
  estado: string;
}

export const ModulesService = {
  getModules: async () => {
    const { data } = await apiAuth.get('/api/modules/');
    return data;
  },

  createModule: async (payload: { nombre: string; descripcion?: string }) => {
    const { data } = await apiAuth.post('/api/modules/', payload);
    return data;
  },

  updateModule: async (id: string, payload: { nombre?: string; descripcion?: string }) => {
    const { data } = await apiAuth.put(`/api/modules/${id}`, payload);
    return data;
  },

  deleteModule: async (id: string) => {
    const { data } = await apiAuth.delete(`/api/modules/${id}`);
    return data;
  }
};
