import { apiAuth } from '../lib/api';

export interface Menu {
  id: string;
  texto: string;
  url?: string;
  icono?: string;
  orden?: string;
  parent_id?: string;
  estado: string;
}

export const MenusService = {
  getMenus: async () => {
    const { data } = await apiAuth.get('/api/menus/');
    return data;
  },

  getMenuTree: async () => {
    const { data } = await apiAuth.get('/api/menus/tree');
    return data;
  },

  createMenu: async (payload: { texto: string; url?: string; icono?: string; orden?: string; parent_id?: string }) => {
    const { data } = await apiAuth.post('/api/menus/', payload);
    return data;
  },

  deleteMenu: async (id: string) => {
    const { data } = await apiAuth.delete(`/api/menus/${id}`);
    return data;
  }
};
