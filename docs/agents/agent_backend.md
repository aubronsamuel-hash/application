# AGENT.backend.md — Version poussée (v2)

Document de référence ultra‑complet pour l’agent Backend (Codex). Tout est structuré pour un usage direct en CI/CD, avec politiques, prompts, checklists, runbooks, et extraits prêts à coller. Code/snippets en ASCII only; la doc peut contenir des accents.

---

## 0) Objectifs clefs
- Robustesse: API stable, idempotente, versionnée, traçable.
- Qualité: tests et couverture bloquante (>= 70 %, cible 85 %), lint/typecheck, guards stricts.
- Observabilité: logs JSON, métriques Prometheus, traces OTLP.
- Sécurité: JWT + RBAC, en-têtes de sécurité, secrets .env, durcissement minimal par défaut.
- Windows‑first: scripts PowerShell 7+ reproduisibles.

## 1) Périmètre
- Stack: FastAPI + SQLAlchemy 2.x + Alembic + Pydantic v2, Postgres, Redis; Celery (optionnel) pour jobs asynchrones; exporter OpenAPI.
- Domaines: utilisateurs, rôles, permissions, missions, planning, disponibilités, timesheets, paie (cachets/heures), exports (CSV/PDF/ICS), notifications, analytics, moteur d’assignation, détection de conflits.

## 2) Principes de design
- DDD light: modules `api/`, `models/`, `schemas/`, `services/`, `core/`.
- Couche service = logique métier; couche API = orchestration/validation; modèles = persistance.
- Erreurs standardisées `{detail, code, meta}`; trace corrélée via `X-Request-ID`.
- Limites raisonnables: taille payload, timeouts client, pagination par défaut.

## 3) Arborescence de référence
```
src/app/
  core/
    config.py
    logging.py
    security.py
  db/
    base.py
    session.py
  models/
    __init__.py
    user.py role.py permission.py
    project.py mission.py assignment.py
    availability.py planning.py
    timesheet.py payroll.py
  schemas/
    user.py mission.py planning.py timesheet.py payroll.py
  services/
    auth.py users.py missions.py planning.py
    assignment.py conflicts.py exports.py notifications.py
  api/
    deps.py
    v1/
      __init__.py
      health.py auth.py users.py missions.py planning.py timesheets.py payroll.py
  scripts/
    seed.py
main.py
```

## 4) Configuration & .env.example
```
APP_ENV=dev
APP_HOST=0.0.0.0
APP_PORT=8000
DATABASE_URL=postgresql+psycopg://user:pass@db:5432/app
REDIS_URL=redis://redis:6379/0
JWT_SECRET=change_me
JWT_EXPIRE_MINUTES=60
CORS_ORIGINS=http://localhost:5173
SMTP_HOST=localhost
SMTP_PORT=1025
SMTP_USER=
SMTP_PASSWORD=
TELEGRAM_BOT_TOKEN=
TELEGRAM_CHAT_ID=
```

## 5) Conventions API
- Base: `/api/v1` (et `/api/v2` en cas de breaking changes).
- Pagination: `page,size`; réponse `{items,total,page,size}`.
- Filtrage: query params simples, ISO dates.
- Idempotency-Key: support sur POST critiques.
- Headers sécurité: `X-Content-Type-Options: nosniff`, `X-Frame-Options: DENY`, HSTS si TLS, CSP minimal côté API.

## 6) Modèles (extraits)
```python
# src/app/models/user.py
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, String, Boolean
from src.app.db.base import Base

class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
```
```python
# src/app/models/mission.py
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, String, DateTime, Boolean, ForeignKey
from src.app.db.base import Base

class Mission(Base):
    __tablename__ = "missions"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    venue: Mapped[str] = mapped_column(String(200))
    start_at: Mapped[DateTime] = mapped_column(nullable=False)
    end_at: Mapped[DateTime] = mapped_column(nullable=False)
    is_payed: Mapped[bool] = mapped_column(Boolean, default=False)
    project_id: Mapped[int | None] = mapped_column(ForeignKey("projects.id"))
```

## 7) Schémas (extraits)
```python
# src/app/schemas/mission.py
from pydantic import BaseModel, field_validator
from datetime import datetime

class MissionCreate(BaseModel):
    title: str
    venue: str | None = None
    start_at: datetime
    end_at: datetime
    @field_validator("end_at")
    @classmethod
    def check_range(cls, v, values):
        if "start_at" in values and v <= values["start_at"]:
            raise ValueError("end_at must be greater than start_at")
        return v
```

## 8) Endpoints v1 (exemple)
```
GET  /api/v1/health
POST /api/v1/auth/login
POST /api/v1/auth/refresh
GET  /api/v1/users
POST /api/v1/users
GET  /api/v1/missions
POST /api/v1/missions
POST /api/v1/assignments/auto
GET  /api/v1/planning/day
GET  /api/v1/planning/week
POST /api/v1/timesheets/close
GET  /api/v1/exports/ics
```

## 9) Politique d’erreurs
- Structure: `{detail: str, code: str, meta: dict}`.
- Codes suggérés: `AUTH_INVALID`, `AUTH_FORBIDDEN`, `VALIDATION_ERR`, `ENTITY_NOT_FOUND`, `CONFLICT_TIME_OVERLAP`, `RATE_LIMITED`, `INTERNAL_ERR`.
- Journaliser l’exception côté serveur avec correlation‑id.

## 10) Sécurité
- Auth: JWT HS256; renouvellement via refresh; rotation des tokens côté client.
- RBAC: roles `admin`, `manager`, `tech`, `viewer`; permissions fines par ressource.
- Inputs: validation stricte Pydantic; filtrage des champs; taille max body.
- Secrets: jamais en dur; .env + vault si dispo; rotation planifiée.
- Durcissement: rate limiting par IP/org (via Redis), anti‑bruteforce login.

## 11) Observabilité
- Logs: `logging.dictConfig` JSON, niveau par module, `X-Request-ID`.
- Prometheus: `prometheus_fastapi_instrumentator` exposé `/metrics`.
- OpenTelemetry: traces OTLP; attributs enrichis (route, status_code, user_id si connu).

## 12) Performance & budgets
- P95 < 400 ms routes clés; P99 < 800 ms; 5xx < 0.5 %/jour.
- DB: < 15 requêtes/endpoint; index sur dates/FK; éviter N+1.
- Cache Redis pour listes/plannings lourds; TTL 60‑300 s.

## 13) Moteur d’assignation (cadre)
- Entrées: besoins mission, disponibilités, contraintes légales repos, affinités/coûts.
- Sortie: plan d’assignation avec score et explications (auditables).
- Implémentation v1: heuristique gloutonne + amélioration locale optionnelle; journal d’explication par contrainte.

## 14) Détection de conflits
- Overlaps technicien, double booking salle, repos légal, incompatibilités rôle.
- `services/conflicts.py` expose `find_conflicts(planning) -> list[Conflict]`.

## 15) Exports & notifications
- Exports: CSV, PDF, ICS; tous horodatés; checksum pour audit.
- Notifications: SMTP/Telegram; journalisées (idempotence par clé).

## 16) Scripts PowerShell (extraits)
```
# tools/dev/dev_up.ps1
param([switch]$WithSeed)
$ErrorActionPreference = "Stop"
Write-Host "Starting dev stack..."
docker compose -f docker/docker-compose.dev.yml up -d --build
if ($WithSeed) { pwsh -File tools/dev/seed.ps1 }

# tools/guards/run_all_guards.ps1
$ErrorActionPreference = "Stop"
& pwsh -File tools/guards/roadmap_guard.ps1 --strict
& pwsh -File tools/guards/commit_guard.ps1 --strict
```

## 17) Workflows CI (durcis)
```
# .github/workflows/backend-tests.yml
name: Codex CI / backend-tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-24.04
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: '3.12' }
      - name: Cache pip
        uses: actions/cache@v4
        with:
          path: ~/.cache/pip
          key: pip-${{ runner.os }}-${{ hashFiles('**/requirements*.txt') }}
      - name: Install
        run: |
          python -m pip install -U pip
          pip install -r requirements.txt
      - name: Lint
        run: ruff check .
      - name: Typecheck (optional)
        run: echo "skip mypy for now"
      - name: Tests + coverage
        run: pytest --cov=src/app --cov-report=xml
      - name: Coverage gate >= 70%
        run: |
          python - <<'PY'
import sys, xml.etree.ElementTree as ET
r = ET.parse('coverage.xml').getroot()
rate = float(r.get('line-rate')) * 100
print(f"Coverage: {rate:.2f}%")
sys.exit(0 if rate >= 70.0 else 1)
PY
```
```
# .github/workflows/guards.yml
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

## 18) Guards PowerShell (durcis)
```
# tools/guards/roadmap_guard.ps1
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
```
# tools/guards/commit_guard.ps1
param([switch]$Strict)
$ErrorActionPreference = "Stop"
$path = "docs/codex/last_output.json"
if (-not (Test-Path $path)) { Write-Host "No last_output.json; skipping."; exit 0 }
try { $null = Get-Content $path -Raw | ConvertFrom-Json } catch { Write-Error "Invalid JSON in $path." }
Write-Host "commit_guard OK"
```

## 19) PR template minimal
```
# .github/PULL_REQUEST_TEMPLATE.md
## Summary
- ...

## Testing
- ...

Ref: docs/roadmap/step-XX.md
```

## 20) Runbooks incidents
- 5xx en hausse: vérifier métriques, logs corrélés, DB pool; rollback si besoin.
- Migrations échouées: `alembic downgrade -1`, patch, `upgrade head`, ajouter tests de migration.
- Couverture en dessous du seuil: prioriser tests manquants; marqueurs `@pytest.mark.slow` autorisés hors CI rapide.

## 21) Checklists PR
- [ ] Lint OK
- [ ] Tests OK, couverture >= 70 %
- [ ] `Ref: docs/roadmap/step-XX.md` présent
- [ ] OpenAPI à jour si endpoints modifiés
- [ ] Docs et runbooks mis à jour

## 22) Roadmap (20 étapes, sous‑étapes X.Y si CI KO)
1. Health + scaffold
2. DB base + Alembic init
3. Auth JWT + seed admin + RBAC minimal
4. Missions CRUD + Users relations
5. Planning day/week datasources
6. Disponibilités + règles de base
7. Timesheets + calcul simple
8. Payroll draft + exports CSV
9. Notifications (SMTP/Telegram)
10. Exports ICS + PDF
11. Assignment v1 + conflits basiques
12. Assignment v1.1 + explications
13. Analytics KPI
14. Observabilité complète
15. Sécurité renforcée
16. Performance pass
17. Multi‑tenancy logique
18. Webhooks + idempotence
19. Hardening CI (k6, audit deps, image scan)
20. Stabilisation LTS + SLA/SLO

## 23) Prompts Codex prêts-à-coller
```
PROMPT.backend.step-N.md
SYSTEM
Tu es Codex Backend. Tu livres du code ASCII only, testé et déterministe. Tu dois faire passer les guards et la CI (couverture >= 70 %). Ajoute la ligne Ref dans le commit/PR.

USER
Contexte: <scope exact de l’étape N>
Attendus:
- code sous src/app/... (liste)
- migration Alembic si besoin
- tests pytest (liste)
- mise à jour README/CHANGELOG si nécessaire
CI/GUARDS:
- run ./tools/guards/run_all_guards.ps1
- coverage >= 70%
Commit:
chore(step-N): <résumé>
Ref: docs/roadmap/step-N.md

ACCEPTANCE
- Lint/Tests OK, couverture >= 70%
- OpenAPI à jour
```
```
PROMPT.backend.fix-guards.md
SYSTEM
Tu es Codex Backend. Corrige les guards (roadmap ref, PR template, last_output.json) sans dégrader la CI.

USER
Logs: <coller logs>
Actions:
- patch tools/guards/*.ps1
- créer/patcher .github/PULL_REQUEST_TEMPLATE.md
- si remote manquant: configurer origin; créer commit vide avec Ref; push
- fallback SSH->HTTPS si push SSH échoue
Commit:
chore(ci): fix guards to unblock PR
Ref: docs/roadmap/step-XX.md
```

## 24) Annexes pratiques
- Exemples curl/httpie, snippets VSCode REST.
- Matrice de compatibilité: Python 3.12+, Ubuntu 24.04 runner.
- Politique de versions: SemVer API par namespace (`/v1`, `/v2`).

Fin.

