import { useState } from "react";
import { adminLogin } from "@/api/auth";

const ADMIN_TOKEN_KEY = "next-track-admin-token";

export function useAdminAuth() {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const login = async (username: string, password: string) => {
    setIsLoading(true);
    setError(null);

    try {
      const response = await adminLogin({ username, password });

      const token = response.access_token || response.token || null;

      if (token) {
        localStorage.setItem(ADMIN_TOKEN_KEY, token);
      }

      return response;
    } catch (err) {
      const message = err instanceof Error ? err.message : "Login failed";
      setError(message);
      throw err;
    } finally {
      setIsLoading(false);
    }
  };

  return {
    login,
    isLoading,
    error,
  };
}