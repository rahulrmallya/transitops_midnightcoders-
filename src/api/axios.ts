import axios, { type AxiosRequestConfig } from "axios";
import { toast } from "sonner";
import { clearAuthStorage, getAccessToken, setAccessToken } from "@/lib/auth-storage";

export const AUTH_LOGOUT_EVENT = "transitops:auth-logout";

type RetryableRequest = AxiosRequestConfig & {
  _retry?: boolean;
};

type TokenRefreshHandler = () => Promise<string | null>;

let tokenRefreshHandler: TokenRefreshHandler | null = null;
let refreshPromise: Promise<string | null> | null = null;

export const api = axios.create({
  baseURL: "http://localhost:8000/api/v1",
  headers: {
    "Content-Type": "application/json",
  },
});

export function setTokenRefreshHandler(handler: TokenRefreshHandler | null) {
  tokenRefreshHandler = handler;
}

function notifyLogout() {
  if (typeof window === "undefined") return;
  window.dispatchEvent(new Event(AUTH_LOGOUT_EVENT));
}

api.interceptors.request.use((config) => {
  const token = getAccessToken();
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const status = error.response?.status;
    const originalRequest = error.config as RetryableRequest | undefined;
    const isLoginRequest = originalRequest?.url?.includes("/auth/login");

    if (status === 401 && originalRequest && !isLoginRequest && !originalRequest._retry) {
      originalRequest._retry = true;

      if (tokenRefreshHandler) {
        refreshPromise ??= tokenRefreshHandler().finally(() => {
          refreshPromise = null;
        });

        const refreshedToken = await refreshPromise;
        if (refreshedToken) {
          setAccessToken(refreshedToken);
          originalRequest.headers = originalRequest.headers ?? {};
          originalRequest.headers.Authorization = `Bearer ${refreshedToken}`;
          return api(originalRequest);
        }
      }

      clearAuthStorage();
      toast.error("Your session has expired. Please sign in again.");
      notifyLogout();
    }

    return Promise.reject(error);
  },
);

export default api;
