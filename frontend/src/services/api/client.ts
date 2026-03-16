import { getAdminToken, removeAdminToken } from '@/lib/storage';

const API_BASE = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8950';

type RequestOptions = RequestInit & {
    headers?: Record<string, string>;
};

export async function apiRequest<T>(path: string, options: RequestOptions = {}): Promise<T> {
    const token = getAdminToken();

    const res = await fetch(`${API_BASE}${path}`, {
        ...options,
        credentials: 'include',
        headers: {
            Accept: 'application/json',
            ...(options.headers || {}),
            ...(token ? { Authorization: `Bearer ${token}` } : {}),
        },
    });

    const contentType = res.headers.get('content-type') || '';
    const isJson = contentType.includes('application/json');
    const data = isJson ? await res.json() : await res.text();

    if (!res.ok) {
        if (res.status === 401) {
            removeAdminToken();
        }

        const err: any = new Error(
            typeof data === 'object' && data?.detail ? data.detail : `HTTP ${res.status}`
        );
        err.status = res.status;
        err.body = data;
        throw err;
    }

    return data as T;
}