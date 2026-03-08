import axios, { type AxiosInstance, type AxiosError } from 'axios';
import type { ApiError } from '@/types';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8110';

export const apiClient: AxiosInstance = axios.create({
  baseURL: `${API_BASE_URL}/api/v1`,
  timeout: 15000,
  headers: { 'Content-Type': 'application/json' },
});

// Auth interceptor
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('next_track_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Error interceptor
apiClient.interceptors.response.use(
  (response) => response,
  (error: AxiosError<ApiError>) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('next_track_token');
      // Could dispatch auth event here
    }
    return Promise.reject(error);
  }
);
