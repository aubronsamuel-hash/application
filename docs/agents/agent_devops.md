# AGENT.devops.md — Version ultra‑poussée (v3)

Document de référence complet pour l’agent **DevOps du Codex**. Conçu pour un usage autonome par Codex et reproductible par des contributeurs humains. Contient objectifs, périmètre, architecture, conventions, scripts Windows‑first, CI/CD durcie, observabilité, guards, prompts, runbooks, checklists. **ASCII only** pour le code et chemins.

---

## 0) Objectifs clefs
- **Disponibilite**: CI/CD verte en < 5 min, rollback en < 1 min.
- **Reproductibilite**: stack docker-compose dev/prod identique, scripts PowerShell Windows-first.
- **Observabilite**: logs centralises Loki, metriques Prometheus, traces OpenTelemetry.
- **Securite**: audits deps/images, scans secrets, RBAC GitHub, TLS partout, headers stricts via proxy.
- **Resilience**: restart auto containers, readiness/liveness checks, backup Postgres + restore test.

---

## 1) Perimetre
- **CI/CD**: GitHub Actions avec workflows backend, frontend, docs, guards, storybook, lighthouse, load tests.
- **Infra locale**: Docker Compose (dev et prod), Caddy reverse proxy, Postgres, Redis, Loki, Prometheus, Grafana.
- **Environnements**: dev (compose.dev), prod (compose.prod), CI (actions runner Ubuntu 24.04).
- **Monitoring**: Prometheus scraping backend/frontend/infra, Grafana dashboards, Loki logs.
- **Alerting**: budget simple (500ms P95, <1% 5xx/jour), alertmanager (optionnel futur).

---

## 2) Principes de design
- **IaC minimaliste**: docker-compose + fichiers yaml versionnes.
- **Windows-first**: scripts .ps1 orchestrent docker/dev/test/guards.
- **Fail fast**: guards stoppent PR avant merge.
- **Security by default**: TLS force par Caddy, secrets en .env, scans images et deps.
- **Observabilite native**: tout service expose /metrics, logs stdout JSON.

---

## 3) Arborescence de reference
```
docker/
  docker-compose.dev.yml
  docker-compose.prod.yml
  caddy/
    Caddyfile.dev
    Caddyfile.prod
  prometheus/
    prometheus.yml
  grafana/
    dashboards/
  loki/
    config.yml
.github/workflows/
  backend-tests.yml
  frontend-tests.yml
  guards.yml
  storybook.yml
  lighthouse.yml
  loadtest.yml
tools/dev/
  dev_up.ps1
  dev_down.ps1
  seed.ps1
  smoke.ps1
tools/guards/
  run_all_guards.ps1
  roadmap_guard.ps1
  commit_guard.ps1
  storybook_guard.ps1
  coverage_guard.ps1
```

---

## 4) Docker Compose (extraits)
```yaml
# docker/docker-compose.dev.yml
version: "3.9"
services:
  backend:
    build: ../
    command: uvicorn src.app.main:app --reload --host 0.0.0.0 --port 8000
    volumes: ["../src:/app/src"]
    env_file: ["../.env"]
    depends_on: [db, redis]
  frontend:
    build: ../frontend
    command: pnpm dev --host
    volumes: ["../frontend:/app"]
    env_file: ["../.env"]
  db:
    image: postgres:16
    environment:
      POSTGRES_USER: user
      POSTGRES_PASSWORD: pass
      POSTGRES_DB: app
    volumes: ["db_data:/var/lib/postgresql/data"]
  redis:
    image: redis:7
  caddy:
    image: caddy:2
    volumes:
      - ./caddy/Caddyfile.dev:/etc/caddy/Caddyfile
    ports: ["80:80", "443:443"]
volumes:
  db_data:
```

---

## 5) Scripts PowerShell (Windows-first)
```ps1
# tools/dev/dev_up.ps1
param([switch]$WithSeed)
$ErrorActionPreference = "Stop"
Write-Host "Starting dev stack..."
docker compose -f docker/docker-compose.dev.yml up -d --build
if ($WithSeed) { pwsh -File tools/dev/seed.ps1 }

# tools/dev/dev_down.ps1
$ErrorActionPreference = "Stop"
Write-Host "Stopping dev stack..."
docker compose -f docker/docker-compose.dev.yml down -v

# tools/dev/smoke.ps1
$ErrorActionPreference = "Stop"
Write-Host "Running smoke tests..."
curl http://localhost:8000/api/v1/health || throw "Backend health fail"
curl http://localhost:5173 || throw "Frontend fail"
```

---

## 6) Workflows CI (extraits durcis)
```yml
# .github/workflows/obs-smoke.yml
name: Codex CI / obs-smoke
on: [pull_request]
jobs:
  obs:
    runs-on: ubuntu-24.04
    steps:
      - uses: actions/checkout@v4
      - name: Boot infra (smoke)
        run: |
          docker compose -f docker/docker-compose.dev.yml up -d db redis
          sleep 5
      - name: Run smoke.ps1
        shell: pwsh
        run: ./tools/dev/smoke.ps1
```

```yml
# .github/workflows/loadtest.yml
name: Codex CI / k6-smoke
on: [pull_request]
jobs:
  k6:
    runs-on: ubuntu-24.04
    steps:
      - uses: actions/checkout@v4
      - uses: grafana/setup-k6-action@v1
      - run: k6 run tests/k6/smoke.js
```

---

## 7) Observabilite
- **Prometheus**: scrape backend `/metrics`, frontend web vitals, Redis/DB exporters.
- **Grafana**: dashboards predefinis (API latency, error rate, DB load, Redis ops, frontend vitals).
- **Loki**: centralisation stdout JSON, queries via labels (service, env, correlation_id).
- **OTLP**: backend traces envoyees a collector (optionnel).

---

## 8) Guards DevOps
```ps1
# tools/guards/coverage_guard.ps1
$ErrorActionPreference = "Stop"
if (-not (Test-Path "coverage/coverage-summary.json")) {
  Write-Error "No coverage summary found"
}
$json = Get-Content coverage/coverage-summary.json | ConvertFrom-Json
$cov = $json.total.lines.pct
if ($cov -lt 70) { Write-Error "Coverage below 70%: $cov" }
Write-Host "coverage_guard OK ($cov %)"
```

---

## 9) Checklists PR
- [ ] Lint OK backend/frontend
- [ ] Tests OK, coverage >= 70 %
- [ ] Ref: docs/roadmap/step-XX.md present
- [ ] Storybook build OK
- [ ] Lighthouse >= 90
- [ ] Observabilite smoke OK
- [ ] No critical CVE deps/images

---

## 10) Runbooks incidents
- **DB crash**: restore backup, alembic upgrade, smoke test.
- **Redis down**: restart container, verify persistence.
- **Backend 5xx spike**: check Loki logs, Prometheus P95 latency, rollback.
- **CI blocked guards**: patch scripts, commit avec Ref obligatoire.
- **Image vuln**: upgrade base image, rerun scans.

---

## 11) Roadmap DevOps (20 etapes)
1. Scaffold docker-compose dev + scripts ps1
2. Add postgres + redis + seed script
3. Add Caddy reverse proxy + TLS dev
4. Add prometheus + scrape backend
5. Add grafana dashboards basiques
6. Add loki + promtail pour logs
7. Add coverage_guard dans guards
8. CI smoke backend/frontend health
9. Add storybook_guard integration
10. Add lighthouse CI job
11. Add k6 smoke loadtest job
12. Add deps audit (npm/pip)
13. Add image scan (docker scout/trivy)
14. Add OpenTelemetry collector
15. Add alertmanager basic rules
16. Add backup Postgres + restore job
17. Add multi-env config (staging/prod)
18. Add CD pipeline prod deploy
19. Add chaos test basic (kill container)
20. Stabilisation LTS infra

---

## 12) Prompts Codex prets-a-coller
```md
PROMPT.devops.step-N.md
SYSTEM
Tu es Codex DevOps. Tu livres des fichiers ascii only (yml, ps1, Dockerfile). Tu dois faire passer lint, guards, CI (smoke, coverage >= 70%, storybook, lighthouse). Ajoute Ref obligatoire.

USER
Contexte: <scope exact de l’etape N>
Attendus:
- docker-compose et fichiers infra
- scripts PowerShell outilles
- workflows CI YAML
- docs README si necessaire
CI/GUARDS:
- run ./tools/guards/run_all_guards.ps1
- coverage >= 70%, Lighthouse >= 90, smoke OK
Commit:
chore(step-N): <resume>
Ref: docs/roadmap/step-N.md

ACCEPTANCE
- CI verte (backend, frontend, guards, obs, storybook, lighthouse, loadtest)
- Smoke tests OK
```

```md
PROMPT.devops.fix-guards.md
SYSTEM
Tu es Codex DevOps. Corrige les guards/CI (obs, smoke, coverage, lighthouse) sans degrader la qualite.

USER
Logs: <coller logs>
Actions:
- patch tools/guards/*.ps1
- patch .github/workflows/*.yml
- ajouter commit Ref vide si manquant
- fallback SSH->HTTPS si push echoue
Commit:
chore(ci): fix devops guards to unblock PR
Ref: docs/roadmap/step-XX.md
```

---

## 13) Annexes pratiques
- **Compat**: Docker Desktop Win11+, WSL2, Ubuntu 24.04 runner.
- **Secrets**: .env + GitHub secrets; jamais commit.
- **Politique versions**: semver infra (v1 devops LTS au step 20).
- **Docs**: dashboards screenshots a stocker sous docs/obs.

---

# ✅ Resume
- AGENT.devops.md = reference complete CI/CD + infra + observabilite.
- Scripts Windows-first PowerShell.
- Workflows CI durs, guards stricts.
- Roadmap 20 etapes.
- Prompts Codex prets a coller.

Fin.

