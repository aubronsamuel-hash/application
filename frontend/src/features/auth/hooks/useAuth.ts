import { useCallback, useMemo } from 'react';

import { useAuthStore } from '../store/auth';

const API_URL = import.meta.env.VITE_API_URL ?? 'http://localhost:8000/api/v1';

interface LoginPayload {
  email: string;
  password: string;
}

interface LoginResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

export function useAuth() {
  const tokens = useAuthStore((state) => state.tokens);
  const setTokens = useAuthStore((state) => state.setTokens);
  const clear = useAuthStore((state) => state.clear);

  const login = useCallback(
    async ({ email, password }: LoginPayload) => {
      const response = await fetch(`${API_URL}/auth/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password }),
      });

      if (!response.ok) {
        throw new Error('Invalid credentials');
      }

      const data: LoginResponse = await response.json();
      setTokens({ accessToken: data.access_token, refreshToken: data.refresh_token });
      return data;
    },
    [setTokens],
  );

  const refresh = useCallback(
    async (refreshToken: string) => {
      const response = await fetch(`${API_URL}/auth/refresh`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ refresh_token: refreshToken }),
      });

      if (!response.ok) {
        throw new Error('Unable to refresh token');
      }

      const data: LoginResponse = await response.json();
      setTokens({ accessToken: data.access_token, refreshToken: data.refresh_token });
      return data;
    },
    [setTokens],
  );

  const logout = useCallback(() => {
    clear();
  }, [clear]);

  const isAuthenticated = useMemo(() => Boolean(tokens?.accessToken), [tokens?.accessToken]);

  return { tokens, isAuthenticated, login, refresh, logout };
}
