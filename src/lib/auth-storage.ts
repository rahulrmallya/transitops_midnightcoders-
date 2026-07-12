export interface AuthUser {
  id: number;
  full_name: string;
  email: string;
  role: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

const ACCESS_TOKEN_KEY = "transitops.access_token";
const USER_KEY = "transitops.user";

function canUseStorage() {
  return typeof window !== "undefined" && typeof window.localStorage !== "undefined";
}

export function getAccessToken() {
  if (!canUseStorage()) return null;
  return window.localStorage.getItem(ACCESS_TOKEN_KEY);
}

export function setAccessToken(token: string) {
  if (!canUseStorage()) return;
  window.localStorage.setItem(ACCESS_TOKEN_KEY, token);
}

export function getStoredUser(): AuthUser | null {
  if (!canUseStorage()) return null;
  const value = window.localStorage.getItem(USER_KEY);
  if (!value) return null;

  try {
    return JSON.parse(value) as AuthUser;
  } catch {
    window.localStorage.removeItem(USER_KEY);
    return null;
  }
}

export function setStoredUser(user: AuthUser) {
  if (!canUseStorage()) return;
  window.localStorage.setItem(USER_KEY, JSON.stringify(user));
}

export function clearAuthStorage() {
  if (!canUseStorage()) return;
  window.localStorage.removeItem(ACCESS_TOKEN_KEY);
  window.localStorage.removeItem(USER_KEY);
}
