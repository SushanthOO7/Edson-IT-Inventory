const tokenKey = "it_inventory_token";

export function getStoredToken(): string | null {
  if (typeof window === "undefined") {
    return null;
  }
  return window.localStorage.getItem(tokenKey);
}

export function setStoredToken(token: string): void {
  window.localStorage.setItem(tokenKey, token);
}

export function clearStoredToken(): void {
  window.localStorage.removeItem(tokenKey);
}
