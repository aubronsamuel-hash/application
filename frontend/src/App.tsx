function App() {
  return (
    <main className="flex flex-col items-center justify-center gap-4 px-4 py-12 text-center">
      <span className="rounded-full bg-sky-500/10 px-4 py-1 text-sm font-semibold uppercase tracking-wide text-sky-300">
        Codex
      </span>
      <h1 className="text-4xl font-bold text-slate-100 sm:text-5xl">Monorepo scaffold ready</h1>
      <p className="max-w-xl text-base text-slate-300 sm:text-lg">
        Backend, frontend and guards are configured. Run the automated tests to keep the health of the project in check.
      </p>
    </main>
  );
}

export default App;
