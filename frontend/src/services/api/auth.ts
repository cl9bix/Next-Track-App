import { apiClient } from './client';
import type { AuthResponse, LoginCredentials } from '@/types';

export const authApi = {
  // Telegram auth
  telegramAuth: (initData: string) =>
    apiClient.post<AuthResponse>('/auth/telegram', { init_data: initData }).then(r => r.data),

  // Admin/DJ login
  login: (credentials: LoginCredentials) =>
    apiClient.post<AuthResponse>('/auth/login', credentials).then(r => r.data),

  // Verify token
  me: () =>
    apiClient.get('/auth/me').then(r => r.data),

  // Logout
  logout: () =>
    apiClient.post('/auth/logout').then(r => r.data),
};
