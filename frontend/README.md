# Codex Frontend

This package contains the Vite + React + TypeScript frontend used for the Codex monorepo scaffold. It ships with Tailwind CSS, Vitest, and ESLint preconfigured.

## Available scripts

```bash
pnpm dev        # start the Vite dev server
pnpm build      # build the production bundle
pnpm lint       # run ESLint with zero-warning policy
pnpm typecheck  # run TypeScript in noEmit mode
pnpm test       # execute Vitest with coverage output
```

## Testing

Vitest runs in a JSDOM environment and reports coverage to `coverage/` with a JSON summary consumed by the GitHub Actions workflow. The sample test in `src/__tests__/app.spec.tsx` ensures the scaffold message renders.

Ref: docs/roadmap/step-01.md
