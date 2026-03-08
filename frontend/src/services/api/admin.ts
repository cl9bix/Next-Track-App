import { apiClient } from './client';
import type { Club, ClubSettings } from '@/types';

export const adminApi = {
  getClub: () =>
    apiClient.get<Club>('/admin/club').then(r => r.data),

  updateClub: (data: Partial<Club>) =>
    apiClient.patch<Club>('/admin/club', data).then(r => r.data),

  updateSettings: (data: Partial<ClubSettings>) =>
    apiClient.patch<ClubSettings>('/admin/club/settings', data).then(r => r.data),

  getDJs: () =>
    apiClient.get('/admin/djs').then(r => r.data),

  inviteDJ: (data: { username: string; telegram_id?: number }) =>
    apiClient.post('/admin/djs/invite', data).then(r => r.data),

  removeDJ: (djId: string) =>
    apiClient.delete(`/admin/djs/${djId}`).then(r => r.data),
};
