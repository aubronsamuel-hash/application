import { BrowserRouter, Route, Routes } from 'react-router-dom';

import { ProtectedRoute } from './features/auth/components/ProtectedRoute';
import { LoginPage } from './features/auth/pages/LoginPage';

function Dashboard() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center gap-4 bg-slate-950 px-4 py-12 text-center text-slate-100">
      <span className="rounded-full bg-sky-500/10 px-4 py-1 text-sm font-semibold uppercase tracking-wide text-sky-300">
        Codex
      </span>
      <h1 className="text-4xl font-bold sm:text-5xl">Tableau de bord protégé</h1>
      <p className="max-w-xl text-base text-slate-300 sm:text-lg">
        Vous êtes authentifié. Ce tableau de bord est accessible uniquement après connexion.
      </p>
    </main>
  );
}

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<LoginPage />} />
        <Route element={<ProtectedRoute />}>
          <Route path="/" element={<Dashboard />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}

export default App;
