import { apiRequest } from "./client";

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
    admin: AdminUser;
};

export async function adminLogin(params: {
    username: string;
    password: string;
}): Promise<AdminLoginResponse> {
    return apiRequest<AdminLoginResponse>("/api/v1/admin/login", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({
            username: params.username,
            password: params.password,
        }),
        credentials: "include",
    });
}

export async function adminLogout(): Promise<{ status: string }> {
    return apiRequest<{ status: string }>("/admin/logout", {
        method: "POST",
        credentials: "include",
    });
}