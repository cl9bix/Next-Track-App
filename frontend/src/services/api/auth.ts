import { apiRequest } from './client';
import { removeAdminToken, setAdminToken } from '@/lib/storage';

export type AdminUser = {
    id: number;
    username: string;
    display_name?: string | null;
    telegram_id?: number | null;
    role: string;
    club_id: number;
    is_active: boolean;
};

export type AdminLoginResponse = {
    status: string;
    access_token: string;
    token_type: string;
    admin: AdminUser;
};

export async function adminLogin(params: {
    username: string;
    password: string;
}): Promise<AdminLoginResponse> {
    const data = await apiRequest<AdminLoginResponse>('/api/v1/admin/login', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(params),
    });

    if (data.access_token) {
        setAdminToken(data.access_token);
    }

    return data;
}

export async function adminMe(): Promise<AdminUser> {
    return apiRequest<AdminUser>('/api/v1/admin/me', {
        method: 'GET',
    });
}

export async function adminLogout(): Promise<{ status: string }> {
    const data = await apiRequest<{ status: string }>('/api/v1/admin/logout', {
        method: 'POST',
    });

    removeAdminToken();
    return data;
}