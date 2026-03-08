import { create } from 'zustand';
import type { UserRole, TelegramUser } from '@/types';

interface AuthStore {
  token: string | null;
  role: UserRole | null;
  user: TelegramUser | null;
  isAuthenticated: boolean;
  setAuth: (token: string, role: UserRole, user?: TelegramUser) => void;
  clearAuth: () => void;
}

export const useAuthStore = create<AuthStore>((set) => ({
  token: localStorage.getItem('next_track_token'),
  role: localStorage.getItem('next_track_role') as UserRole | null,
  user: null,
  isAuthenticated: !!localStorage.getItem('next_track_token'),

  setAuth: (token, role, user) => {
    localStorage.setItem('next_track_token', token);
    localStorage.setItem('next_track_role', role);
    set({ token, role, user, isAuthenticated: true });
  },

  clearAuth: () => {
    localStorage.removeItem('next_track_token');
    localStorage.removeItem('next_track_role');
    set({ token: null, role: null, user: null, isAuthenticated: false });
  },
}));
