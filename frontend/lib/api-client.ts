import { getStoredToken } from "@/lib/auth-store";

const backendUrl = process.env.NEXT_PUBLIC_BACKEND_URL ?? "http://localhost:8001";

export async function apiFetch(path: string, init?: RequestInit) {
  const token = getStoredToken();
  const response = await fetch(`${backendUrl}${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...(init?.headers ?? {}),
    },
    cache: "no-store",
  });

  if (!response.ok) {
    const payload = (await response.json().catch(() => null)) as { detail?: string } | null;
    throw new Error(payload?.detail ?? `Request failed: ${response.status}`);
  }

  return response.json();
}

export async function apiLogin(email: string, password: string) {
  const response = await fetch(`${backendUrl}/auth/login`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ email, password }),
  });

  if (!response.ok) {
    const payload = (await response.json().catch(() => null)) as { detail?: string } | null;
    throw new Error(payload?.detail ?? `Request failed: ${response.status}`);
  }

  return response.json() as Promise<{ access_token: string; token_type: string }>;
}
