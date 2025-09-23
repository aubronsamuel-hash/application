import { FormEvent, useState } from 'react';

import { useAuth } from '../hooks/useAuth';

export function LoginPage() {
  const { login } = useAuth();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setSubmitting] = useState(false);

  const onSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setError(null);
    setSubmitting(true);
    try {
      await login({ email, password });
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unable to login');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <main className="mx-auto flex min-h-screen max-w-md flex-col justify-center gap-6 px-4 py-12">
      <section className="rounded-lg border border-slate-700 bg-slate-900/60 p-6 shadow-lg">
        <h1 className="text-2xl font-semibold text-slate-100">Connexion</h1>
        <p className="mt-1 text-sm text-slate-400">Connectez-vous pour accéder au tableau de bord.</p>
        <form className="mt-6 flex flex-col gap-4" onSubmit={onSubmit}>
          <label className="flex flex-col gap-2 text-sm text-slate-200">
            Email
            <input
              className="rounded-md border border-slate-700 bg-slate-950 px-3 py-2 text-base text-slate-100 focus:border-sky-500 focus:outline-none"
              name="email"
              type="email"
              autoComplete="email"
              value={email}
              onChange={(event) => setEmail(event.target.value)}
              required
            />
          </label>
          <label className="flex flex-col gap-2 text-sm text-slate-200">
            Mot de passe
            <input
              className="rounded-md border border-slate-700 bg-slate-950 px-3 py-2 text-base text-slate-100 focus:border-sky-500 focus:outline-none"
              name="password"
              type="password"
              autoComplete="current-password"
              value={password}
              onChange={(event) => setPassword(event.target.value)}
              required
            />
          </label>
          {error ? <p className="text-sm text-red-400" role="alert">{error}</p> : null}
          <button
            className="rounded-md bg-sky-500 px-4 py-2 text-sm font-medium text-white transition hover:bg-sky-600 disabled:cursor-not-allowed disabled:bg-sky-500/60"
            type="submit"
            disabled={isSubmitting}
          >
            {isSubmitting ? 'Connexion...' : 'Se connecter'}
          </button>
        </form>
      </section>
    </main>
  );
}
