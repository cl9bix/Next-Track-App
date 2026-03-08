const ADMIN_TOKEN_KEY = 'next-track-admin-token';

export const storage = {
  getAdminToken(): string | null {
    return localStorage.getItem(ADMIN_TOKEN_KEY);
  },

  setAdminToken(token: string) {
    localStorage.setItem(ADMIN_TOKEN_KEY, token);
  },

  removeAdminToken() {
    localStorage.removeItem(ADMIN_TOKEN_KEY);
  },
};