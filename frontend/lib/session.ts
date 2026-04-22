const TOKEN_STORAGE_KEY = "sweos.access_token";

export function getStoredToken(): string | null {
  if (typeof window === "undefined") {
    return null;
  }

  return window.localStorage.getItem(TOKEN_STORAGE_KEY);
}

export function setStoredToken(token: string): void {
  if (typeof window === "undefined") {
    return;
  }

  window.localStorage.setItem(TOKEN_STORAGE_KEY, token);
}

export function clearStoredToken(): void {
  if (typeof window === "undefined") {
    return;
  }

  window.localStorage.removeItem(TOKEN_STORAGE_KEY);
}
