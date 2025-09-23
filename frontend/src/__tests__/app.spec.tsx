import { render, screen } from '@testing-library/react';

import App from '../App';

describe('App routing', () => {
  it('renders the login page when not authenticated', () => {
    render(<App />);

    expect(screen.getByRole('heading', { name: /connexion/i })).toBeVisible();
    expect(screen.getByRole('button', { name: /se connecter/i })).toBeEnabled();
  });
});
