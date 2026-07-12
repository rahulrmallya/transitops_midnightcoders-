import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from "react";
import { useNavigate } from "@tanstack/react-router";
import { toast } from "sonner";
import { getCurrentUser, login as loginRequest, type LoginPayload } from "@/api/auth";
import {
  clearAuthStorage,
  getAccessToken,
  getStoredUser,
  setAccessToken,
  setStoredUser,
  type AuthUser,
} from "@/lib/auth-storage";
import { AUTH_LOGOUT_EVENT } from "@/api/axios";

interface AuthContextValue {
  user: AuthUser | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (payload: LoginPayload) => Promise<void>;
  logout: () => void;
  refreshUser: () => Promise<void>;
}

const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const navigate = useNavigate();
  const [token, setToken] = useState<string | null>(() => getAccessToken());
  const [user, setUser] = useState<AuthUser | null>(() => getStoredUser());
  const [isLoading, setIsLoading] = useState(() => Boolean(getAccessToken()));

  const logout = useCallback(() => {
    clearAuthStorage();
    setToken(null);
    setUser(null);
    navigate({ to: "/login", replace: true });
  }, [navigate]);

  const refreshUser = useCallback(async () => {
    const currentUser = await getCurrentUser();
    setStoredUser(currentUser);
    setUser(currentUser);
  }, []);

  useEffect(() => {
    const currentToken = getAccessToken();
    if (!currentToken) {
      setIsLoading(false);
      return;
    }

    let active = true;
    setIsLoading(true);
    refreshUser()
      .catch(() => {
        if (!active) return;
        clearAuthStorage();
        setToken(null);
        setUser(null);
      })
      .finally(() => {
        if (active) setIsLoading(false);
      });

    return () => {
      active = false;
    };
  }, [refreshUser]);

  useEffect(() => {
    const onLogout = () => {
      clearAuthStorage();
      setToken(null);
      setUser(null);
      navigate({ to: "/login", replace: true });
    };

    window.addEventListener(AUTH_LOGOUT_EVENT, onLogout);
    return () => window.removeEventListener(AUTH_LOGOUT_EVENT, onLogout);
  }, [navigate]);

  const login = useCallback(
    async (payload: LoginPayload) => {
      const auth = await loginRequest(payload);
      setAccessToken(auth.access_token);
      setStoredUser(auth.user);
      setToken(auth.access_token);
      setUser(auth.user);
      toast.success("Signed in successfully");
      navigate({ to: "/dashboard", replace: true });
    },
    [navigate],
  );

  const value = useMemo<AuthContextValue>(
    () => ({
      user,
      token,
      isAuthenticated: Boolean(token && user),
      isLoading,
      login,
      logout,
      refreshUser,
    }),
    [isLoading, login, logout, refreshUser, token, user],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within AuthProvider");
  }
  return context;
}
