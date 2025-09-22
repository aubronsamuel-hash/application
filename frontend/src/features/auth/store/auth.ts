import { create } from 'zustand';

export interface AuthTokens {
  accessToken: string;
  refreshToken: string;
}

interface AuthState {
  tokens: AuthTokens | null;
  setTokens: (tokens: AuthTokens) => void;
  clear: () => void;
}

export const useAuthStore = create<AuthState>((set) => ({
  tokens: null,
  setTokens: (tokens) => set({ tokens }),
  clear: () => set({ tokens: null }),
}));
