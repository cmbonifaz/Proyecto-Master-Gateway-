import { apiAuth } from '../lib/api';

export interface Role {
  id: string;
  nombre: string;
  descripcion: string;
  estado: string;
}

export const RolesService = {
  getRoles: async () => {
    const { data } = await apiAuth.get('/api/roles');
    return data;
  },

  getRoleById: async (id: string) => {
    const { data } = await apiAuth.get(`/api/roles/${id}`);
    return data;
  },

  getRolePermissions: async (id: string) => {
    const { data } = await apiAuth.get(`/api/roles/${id}/permissions`);
    return data; // { users: [...], modules: [...], menus: [...] }
  },

  createRole: async (payload: { nombre: string; descripcion?: string }) => {
    const { data } = await apiAuth.post('/api/roles', payload);
    return data;
  },

  updateRole: async (id: string, payload: { nombre?: string; descripcion?: string }) => {
    const { data } = await apiAuth.put(`/api/roles/${id}`, payload);
    return data;
  },

  deleteRole: async (id: string) => {
    const { data } = await apiAuth.delete(`/api/roles/${id}`);
    return data;
  },

  assignUser: async (roleId: string, userId: string) => {
    const { data } = await apiAuth.post(`/api/roles/${roleId}/users?user_id=${userId}`);
    return data;
  },

  unassignUser: async (roleId: string, userId: string) => {
    const { data } = await apiAuth.delete(`/api/roles/${roleId}/users/${userId}`);
    return data;
  },

  assignModule: async (roleId: string, moduleId: string) => {
    const { data } = await apiAuth.post(`/api/roles/${roleId}/modules?module_id=${moduleId}`);
    return data;
  },

  unassignModule: async (roleId: string, moduleId: string) => {
    const { data } = await apiAuth.delete(`/api/roles/${roleId}/modules/${moduleId}`);
    return data;
  },

  assignMenu: async (roleId: string, menuId: string) => {
    const { data } = await apiAuth.post(`/api/roles/${roleId}/menus?menu_id=${menuId}`);
    return data;
  },

  unassignMenu: async (roleId: string, menuId: string) => {
    const { data } = await apiAuth.delete(`/api/roles/${roleId}/menus/${menuId}`);
    return data;
  }
};
