const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL?.replace(/\/+$/, "") || "http://localhost:8000";

type RequestOptions = {
  method?: "GET" | "POST" | "PUT" | "PATCH" | "DELETE";
  headers?: Record<string, string>;
  body?: BodyInit | null;
  authToken?: string | null;
};

export async function apiRequest<T>(
  path: string,
  options: RequestOptions = {}
): Promise<T> {
  const { method = "GET", headers = {}, body, authToken } = options;

  const response = await fetch(`${API_BASE_URL}${path}`, {
    method,
    headers: {
      ...headers,
      ...(authToken ? { Authorization: `Bearer ${authToken}` } : {}),
    },
    body,
    credentials: "include",
  });

  const contentType = response.headers.get("content-type") || "";
  const isJson = contentType.includes("application/json");
  const payload = isJson ? await response.json() : await response.text();

  if (!response.ok) {
    const message =
      typeof payload === "object" && payload !== null && "detail" in payload
        ? typeof payload.detail === "string"
          ? payload.detail
          : JSON.stringify(payload.detail)
        : typeof payload === "string"
          ? payload
          : `Request failed with status ${response.status}`;

    throw new Error(message);
  }

  return payload as T;
}

export { API_BASE_URL };