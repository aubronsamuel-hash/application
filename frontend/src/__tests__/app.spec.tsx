import { render, screen } from '@testing-library/react';

import App from '../App';

describe('App', () => {
  it('renders the scaffold message', () => {
    render(<App />);

    expect(screen.getByText(/monorepo scaffold ready/i)).toBeVisible();
    expect(
      screen.getByText(/Backend, frontend and guards are configured/i),
    ).toBeVisible();
  });
});
