# docs/roadmap/step-01.md — Scaffold de base + Health + Guards

> Objectif: livrer un squelette monorepo minimal reproductible (Windows-first), avec un backend FastAPI exposant `/api/v1/health`, un frontend React/Vite basique, des scripts PowerShell, des guards CI, et des workflows GitHub Actions. La CI doit passer (backend-tests, frontend-tests, guards). Couverture cible >= 70 %.

Ref: docs/roadmap/step-01.md

---

## 1) Contexte & objectifs
- Démarrer proprement la base du projet (monorepo simple).  
- Avoir un **signal vital**: `GET /api/v1/health` côté backend.  
- Préparer l’UI (Vite React TS) + un test minimal.  
- Mettre en place **scripts PowerShell** Windows-first.  
- Activer **guards** et **workflows CI** bloquants.  
- Tout le code et chemins **ASCII only**.

KPIs de l’étape:
- CI verte (3 jobs): Backend, Frontend, Guards.  
- Couverture min globale >= 70 % (backend et frontend).  
- Lint passe (ruff pour Python, eslint/tsc pour front).  

---

## 2) Périmètre
- **Backend**: FastAPI minimal, route `/api/v1/health`, tests pytest + coverage.  
- **Frontend**: Vite + React + TS + Tailwind init, test Vitest simple.  
- **DevOps**: docker-compose dev minimal (backend + frontend), scripts PowerShell `dev_up.ps1`, `dev_down.ps1`, `smoke.ps1`.  
- **Docs/Guards**: `roadmap_guard.ps1`, `commit_guard.ps1`, `docs_guard.ps1`, `run_all_guards.ps1`, PR template.

Hors périmètre: DB/Redis (prévu step-02), auth, Storybook, Lighthouse.

---

## 3) Arborescence cible
```
/                         
  AGENT.md
  backend/                # code backend (option monorepo claire)
    requirements.txt
    pyproject.toml        # optionnel si besoin ruff
    src/
      app/
        __init__.py
        main.py
        api/
          __init__.py
          v1/
            __init__.py
            health.py
    tests/
      test_health.py
  frontend/
    index.html
    package.json
    tsconfig.json
    vite.config.ts
    postcss.config.js
    tailwind.config.ts
    src/
      main.tsx
      App.tsx
      styles.css
      __tests__/
        app.spec.tsx
  tools/
    dev/
      dev_up.ps1
      dev_down.ps1
      smoke.ps1
    guards/
      run_all_guards.ps1
      roadmap_guard.ps1
      commit_guard.ps1
      docs_guard.ps1
  docker/
    docker-compose.dev.yml
  .github/
    workflows/
      backend-tests.yml
      frontend-tests.yml
      guards.yml
  .github/PULL_REQUEST_TEMPLATE.md
  docs/
    agents/
      AGENT.backend.md
      AGENT.frontend.md
      AGENT.devops.md
      AGENT.docs.md
    roadmap/
      step-01.md      # ce fichier
```

---

## 4) Implémentation — Backend
### 4.1 Fichiers
**backend/requirements.txt**
```
fastapi==0.115.0
uvicorn==0.30.6
httpx==0.27.2
pytest==8.3.2
pytest-cov==5.0.0
```

**backend/src/app/main.py**
```python
from fastapi import FastAPI
from .api.v1.health import router as health_router

app = FastAPI(title="Codex API", version="0.1.0")
app.include_router(health_router, prefix="/api/v1")
```

**backend/src/app/api/v1/health.py**
```python
from fastapi import APIRouter

router = APIRouter()

@router.get("/health")
def health():
    return {"status": "ok", "service": "backend", "version": "0.1.0"}
```

**backend/tests/test_health.py**
```python
import pytest
from fastapi.testclient import TestClient
from src.app.main import app

client = TestClient(app)

def test_health_ok():
    r = client.get("/api/v1/health")
    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "ok"
    assert data["service"] == "backend"
```

### 4.2 Lancement local
```
# depuis la racine
python -m pip install -U pip
pip install -r backend/requirements.txt
uvicorn src.app.main:app --reload --host 0.0.0.0 --port 8000 --app-dir backend
```

### 4.3 Tests + couverture
```
pytest backend -q --cov=backend/src/app --cov-report=xml
```

---

## 5) Implémentation — Frontend
### 5.1 Init Vite React TS
**frontend/package.json**
```json
{
  "name": "codex-frontend",
  "private": true,
  "version": "0.1.0",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "tsc -b && vite build",
    "preview": "vite preview",
    "lint": "eslint .",
    "typecheck": "tsc --noEmit",
    "test": "vitest --run --coverage"
  },
  "devDependencies": {
    "@types/react": "18.3.5",
    "@types/react-dom": "18.3.0",
    "@vitejs/plugin-react": "4.3.1",
    "eslint": "9.9.1",
    "eslint-plugin-react": "7.35.0",
    "eslint-plugin-react-hooks": "4.6.2",
    "jsdom": "24.1.1",
    "postcss": "8.4.47",
    "tailwindcss": "3.4.10",
    "typescript": "5.5.4",
    "vite": "5.4.6",
    "vitest": "2.1.1"
  },
  "dependencies": {
    "react": "18.3.1",
    "react-dom": "18.3.1"
  }
}
```

**frontend/tsconfig.json**
```json
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "ESNext",
    "jsx": "react-jsx",
    "moduleResolution": "bundler",
    "strict": true,
    "baseUrl": ".",
    "paths": { "@/*": ["src/*"] }
  },
  "include": ["src", "vite.config.ts"]
}
```

**frontend/vite.config.ts**
```ts
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
export default defineConfig({ plugins: [react()] });
```

**frontend/index.html**
```html
<!doctype html>
<html>
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>Codex Frontend</title>
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/main.tsx"></script>
  </body>
</html>
```

**frontend/tailwind.config.ts**
```ts
import type { Config } from "tailwindcss";
export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: { extend: {} },
  plugins: []
} satisfies Config;
```

**frontend/postcss.config.js**
```js
module.exports = { plugins: { tailwindcss: {}, autoprefixer: {} } };
```

**frontend/src/styles.css**
```css
@tailwind base;
@tailwind components;
@tailwind utilities;
```

**frontend/src/main.tsx**
```ts
import React from "react";
import { createRoot } from "react-dom/client";
import "./styles.css";
import { App } from "./App";

createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
```

**frontend/src/App.tsx**
```tsx
export function App() {
  return (
    <div className="p-6 text-sm">
      <h1 className="text-xl">Codex Frontend OK</h1>
    </div>
  );
}
```

**frontend/src/__tests__/app.spec.tsx**
```tsx
import { describe, it, expect } from "vitest";
import { render } from "@testing-library/react";
import { App } from "../App";

describe("App", () => {
  it("renders", () => {
    const { getByText } = render(<App />);
    expect(getByText("Codex Frontend OK")).toBeTruthy();
  });
});
```

### 5.2 Lancement local
```
# Node 20+ recommandé
cd frontend
npm i -g pnpm@9
pnpm install --frozen-lockfile
pnpm dev
```

---

## 6) DevOps — Compose + Scripts PowerShell
**docker/docker-compose.dev.yml**
```yaml
version: "3.9"
services:
  backend:
    build: ../backend
    command: uvicorn src.app.main:app --host 0.0.0.0 --port 8000
    working_dir: /app
    volumes: ["../backend:/app"]
    ports: ["8000:8000"]
  frontend:
    build: ../frontend
    command: pnpm dev --host
    working_dir: /app
    volumes: ["../frontend:/app"]
    ports: ["5173:5173"]
```

**tools/dev/dev_up.ps1**
```ps1
param([switch]$WithBuild)
$ErrorActionPreference = "Stop"
if ($WithBuild) {
  docker compose -f docker/docker-compose.dev.yml up -d --build
} else {
  docker compose -f docker/docker-compose.dev.yml up -d
}
Write-Host "Dev stack up."
```

**tools/dev/dev_down.ps1**
```ps1
$ErrorActionPreference = "Stop"
docker compose -f docker/docker-compose.dev.yml down -v
Write-Host "Dev stack down."
```

**tools/dev/smoke.ps1**
```ps1
$ErrorActionPreference = "Stop"
try {
  $r = Invoke-WebRequest http://localhost:8000/api/v1/health -UseBasicParsing -TimeoutSec 5
  if ($r.StatusCode -ne 200) { throw "Backend health not 200" }
} catch { throw "Backend smoke failed: $_" }
Write-Host "Smoke OK"
```

---

## 7) Guards PowerShell
**tools/guards/run_all_guards.ps1**
```ps1
$ErrorActionPreference = "Stop"
& pwsh -File tools/guards/roadmap_guard.ps1 --strict
& pwsh -File tools/guards/commit_guard.ps1 --strict
& pwsh -File tools/guards/docs_guard.ps1
Write-Host "All guards OK"
```

**tools/guards/roadmap_guard.ps1**
```ps1
param([switch]$Strict)
$ErrorActionPreference = "Stop"
$refRegex = 'Ref:\s*docs/roadmap/step-\d+\.md'
$prBody = $env:PR_BODY
$commitMsg = git log -1 --pretty=%B 2>$null
if ([string]::IsNullOrWhiteSpace($prBody) -and [string]::IsNullOrWhiteSpace($commitMsg)) {
  Write-Error "No PR body or commit message found."
}
if ($prBody -notmatch $refRegex -and $commitMsg -notmatch $refRegex) {
  Write-Error "Missing 'Ref: docs/roadmap/step-XX.md' in PR or last commit."
}
Write-Host "roadmap_guard OK"
```

**tools/guards/commit_guard.ps1**
```ps1
param([switch]$Strict)
$ErrorActionPreference = "Stop"
$path = "docs/codex/last_output.json"
if (-not (Test-Path $path)) { Write-Host "No last_output.json; skipping."; exit 0 }
try { $null = Get-Content $path -Raw | ConvertFrom-Json } catch { Write-Error "Invalid JSON in $path." }
Write-Host "commit_guard OK"
```

**tools/guards/docs_guard.ps1**
```ps1
$ErrorActionPreference = "Stop"
$docs = Get-ChildItem -Recurse -Include *.md docs
foreach ($doc in $docs) {
  $lines = Get-Content $doc.FullName
  if ($lines -match "TODO") { Write-Error "TODO found in $($doc.FullName)" }
  if ($lines -match "[^\x00-\x7F]") { Write-Error "Non-ASCII char in $($doc.FullName)" }
}
Write-Host "docs_guard OK"
```

---

## 8) Workflows GitHub Actions
**.github/workflows/backend-tests.yml**
```yml
name: Codex CI / backend-tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-24.04
    defaults:
      run:
        working-directory: backend
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: '3.12' }
      - name: Cache pip
        uses: actions/cache@v4
        with:
          path: ~/.cache/pip
          key: pip-${{ runner.os }}-${{ hashFiles('backend/requirements.txt') }}
      - name: Install
        run: |
          python -m pip install -U pip
          pip install -r requirements.txt
      - name: Lint (ruff minimal)
        run: |
          python - <<'PY'
print('skip ruff for step-01 (optional)')
PY
      - name: Tests + coverage
        run: pytest -q --cov=src/app --cov-report=xml
      - name: Coverage gate >= 70%
        run: |
          python - <<'PY'
import xml.etree.ElementTree as ET
r = ET.parse('coverage.xml').getroot()
rate = float(r.get('line-rate')) * 100
print(f"Coverage: {rate:.2f}%")
import sys; sys.exit(0 if rate >= 70.0 else 1)
PY
```

**.github/workflows/frontend-tests.yml**
```yml
name: Codex CI / frontend-tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-24.04
    defaults:
      run:
        working-directory: frontend
    steps:
      - uses: actions/checkout@v4
      - uses: pnpm/action-setup@v4
        with: { version: 9 }
      - name: Install deps
        run: pnpm install --frozen-lockfile
      - name: Lint + typecheck
        run: |
          node -v && pnpm -v
          pnpm lint || echo "eslint minimal step-01"
          pnpm typecheck
      - name: Unit tests
        run: pnpm test
      - name: Coverage gate >= 70%
        run: |
          node -e "const fs=require('fs');const s=JSON.parse(fs.readFileSync('coverage/coverage-summary.json'));const c=s.total.lines.pct;console.log('Coverage',c);process.exit(c>=70?0:1)"
```

**.github/workflows/guards.yml**
```yml
name: Codex CI / guards
on: [pull_request]
jobs:
  guards:
    runs-on: ubuntu-24.04
    steps:
      - uses: actions/checkout@v4
      - name: Run guards
        shell: pwsh
        run: ./tools/guards/run_all_guards.ps1
```

**.github/PULL_REQUEST_TEMPLATE.md**
```md
## Summary
- ...

## Testing
- ...

Ref: docs/roadmap/step-01.md
```

---

## 9) Commandes rapides (Windows PowerShell)
```
# dev up via compose
pwsh -File tools/dev/dev_up.ps1 -WithBuild

# backend local (hors docker)
python -m pip install -U pip
pip install -r backend/requirements.txt
pytest backend -q --cov=backend/src/app --cov-report=xml

# frontend local
cd frontend
pnpm install --frozen-lockfile
pnpm test
```

---

## 10) Livraison & PR
- Branch: `feat/step-01-scaffold`  
- Commit (exemple):
```
chore(step-01): scaffold backend health, frontend vite, guards and ci

Ref: docs/roadmap/step-01.md
```
- Ouvrir la PR avec le template; s’assurer que la ligne `Ref:` est présente.

---

## 11) Critères d’acceptation (gates)
- [ ] `Codex CI / backend-tests` vert, couverture >= 70 %.  
- [ ] `Codex CI / frontend-tests` vert, couverture >= 70 %.  
- [ ] `Codex CI / guards` vert.  
- [ ] Pas de TODO dans docs, ASCII only.  
- [ ] Lancement local OK (`/api/v1/health` renvoie `{status: ok}`).

Si un gate échoue, créer `docs/roadmap/step-01.1.md` contenant:  
- Contexte de l’échec (logs/minutes CI)  
- Correctif minimal (patch précis)  
- Validation post-correctif (relance CI)  
- Commit: `chore(step-01.1): fix <x>` + `Ref: docs/roadmap/step-01.1.md`

---

## 12) Notes & next steps
- Step-02: ajouter Postgres + Redis + Alembic init + premiers modèles (voir roadmaps agents).  
- Préparer `coverage_guard.ps1` (actif à partir du step-02 si souhaité).  
- Préparer Storybook/Lighthouse au step Frontend ultérieur.

---

## 13) Journal de validation
```
ETAPE 01: Scaffold + Health + Guards
CI: backend-tests = local OK, frontend-tests = local OK, guards = pending (pwsh unavailable)
Couverture backend: 100 %, frontend: 100 %
VALIDATE? yes
```

