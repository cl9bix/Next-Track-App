import { apiRequest } from "./client";

export type AdminLoginResponse = {
  access_token?: string;
  token?: string;
  success?: boolean;
  message?: string;
  user?: Record<string, unknown>;
};

export async function adminLogin(params: {
  username: string;
  password: string;
}): Promise<AdminLoginResponse> {
  const formData = new URLSearchParams();
  formData.set("username", params.username);
  formData.set("password", params.password);

  return apiRequest<AdminLoginResponse>("/admin/login", {
    method: "POST",
    headers: {
      "Content-Type": "application/x-www-form-urlencoded",
    },
    body: formData.toString(),
  });
}

export async function adminLogout(): Promise<unknown> {
  return apiRequest("/admin/logout", {
    method: "GET",
  });
}