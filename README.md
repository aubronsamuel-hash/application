# Codex Monorepo Scaffold

This repository provides the baseline scaffolding for the Codex project. It ships a FastAPI backend with a health endpoint, a React + Vite frontend bootstrapped with Tailwind CSS, PowerShell helper scripts, and GitHub Actions workflows guarded by simple quality checks.

## Project structure

- `backend/` – FastAPI application exposing `/api/v1/health` and pytest coverage configuration.
- `frontend/` – React + TypeScript UI with Vitest coverage, ESLint, and Tailwind CSS.
- `tools/dev/` – PowerShell scripts to manage the local Docker Compose stack and smoke tests.
- `tools/guards/` – Guard scripts ensuring roadmap references and ASCII-only documentation.
- `docker/` – Development `docker-compose` definition.
- `.github/workflows/` – CI pipelines for backend, frontend, and guard validation.
- `docs/` – Codex governance, agents, and roadmap documentation.

## Getting started

### Backend

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements.txt
pytest backend
```

### Frontend

```bash
cd frontend
pnpm install
pnpm lint
pnpm typecheck
pnpm test
```

### Docker Compose helpers (PowerShell)

```powershell
pwsh -File tools/dev/dev_up.ps1 -WithBuild
pwsh -File tools/dev/smoke.ps1
pwsh -File tools/dev/dev_down.ps1
```

## Continuous integration

Three GitHub Actions workflows run on each push or pull request:

- **Backend tests** – installs Python dependencies, runs pytest, and enforces a 70 % coverage threshold.
- **Frontend tests** – installs pnpm dependencies, runs lint + typecheck, Vitest with coverage, and checks for 70 % coverage.
- **Guards** – runs roadmap, commit, and documentation PowerShell guards.

Ref: docs/roadmap/step-01.md
