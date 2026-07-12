import api from "./axios";
import type { AuthUser } from "@/lib/auth-storage";

export interface ApiSuccess<T> {
  success: boolean;
  message: string;
  data: T;
}

export interface LoginPayload {
  email: string;
  password: string;
}

export interface LoginResult {
  access_token: string;
  token_type: string;
  user: AuthUser;
}

export async function login(payload: LoginPayload) {
  const response = await api.post<ApiSuccess<LoginResult>>("/auth/login", payload);
  return response.data.data;
}

export async function getCurrentUser() {
  const response = await api.get<ApiSuccess<AuthUser>>("/auth/me");
  return response.data.data;
}
