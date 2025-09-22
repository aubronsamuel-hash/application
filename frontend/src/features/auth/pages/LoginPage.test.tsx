import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { afterEach, beforeEach, expect, vi } from 'vitest';

import { useAuthStore } from '../store/auth';
import { LoginPage } from './LoginPage';

declare global {
  // eslint-disable-next-line no-var
  var fetch: typeof window.fetch;
}

beforeEach(() => {
  useAuthStore.setState({ tokens: null });
});

afterEach(() => {
  vi.restoreAllMocks();
});

describe('LoginPage', () => {
  it('submits credentials and stores tokens', async () => {
    const fetchMock = vi
      .spyOn(global, 'fetch')
      .mockResolvedValue({
        ok: true,
        json: async () => ({ access_token: 'token', refresh_token: 'refresh', token_type: 'bearer' }),
      } as unknown as Response);

    render(<LoginPage />);

    await userEvent.type(screen.getByLabelText(/email/i), 'admin@example.com');
    await userEvent.type(screen.getByLabelText(/mot de passe/i), 'password');
    await userEvent.click(screen.getByRole('button', { name: /se connecter/i }));

    await waitFor(() => {
      expect(useAuthStore.getState().tokens?.accessToken).toBe('token');
    });

    expect(fetchMock).toHaveBeenCalledWith(
      'http://localhost:8000/api/v1/auth/login',
      expect.objectContaining({ method: 'POST' }),
    );
  });

  it('renders an error message when login fails', async () => {
    vi.spyOn(global, 'fetch').mockResolvedValue({
      ok: false,
      json: async () => ({ message: 'error' }),
    } as unknown as Response);

    render(<LoginPage />);

    await userEvent.type(screen.getByLabelText(/email/i), 'admin@example.com');
    await userEvent.type(screen.getByLabelText(/mot de passe/i), 'password');
    await userEvent.click(screen.getByRole('button', { name: /se connecter/i }));

    await waitFor(() => {
      expect(screen.getByRole('alert')).toHaveTextContent(/invalid credentials/i);
    });
  });
});
