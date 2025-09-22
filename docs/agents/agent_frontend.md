# AGENT.frontend.md — Version ultra-poussée (v3)

Document de référence complet pour l’agent Frontend du Codex. Pensé pour l’exécution par un agent autonome (Codex) et pour des contributeurs humains. Inclut objectifs, périmètre, architecture, conventions, scripts Windows-first, CI durcie, guards, prompts, checklists, runbooks, et canevas de composants. ASCII only pour le code et les noms de fichiers.

---

## 0) Objectifs clefs
- Performance: TTFB serveur proxy < 200 ms, LCP < 2.5 s sur connexions typiques, bundle initial < 200 Ko gzip (cible 150 Ko), Lighthouse PWA/Perf/BestPractices/SEO/A11y >= 90.
- Qualité: lint/typecheck stricts, tests unitaires + composant + e2e, coverage global >= 70 % (cible 85 %), pas de warnings console en prod.
- Accessibilite: WCAG 2.1 AA, 0 erreurs critiques axe, navigation clavier totale, contrastes OK.
- Robustesse: error boundaries par page, retry reseau avec backoff, graceful degradation offline.
- Securite: routing protege, sanitization stricte, pas de dangerouslySetInnerHTML, CSP appliquee par reverse proxy, politique d’origines stricte.
- Windows-first: scripts PowerShell 7+ reproductibles; parite CI Linux.

---

## 1) Perimetre
- Stack: React 18, TypeScript 5, Vite 5, Tailwind 3, shadcn/ui, Radix primitives, TanStack Query, Zustand (ou Redux Toolkit) pour etat global, Zod pour validation client, date-fns, recharts, react-hook-form.
- Tests: Vitest + RTL pour unitaires, Playwright pour e2e, axe-core pour a11y.
- Outils UI: Storybook 8, Chromatic pour revue visuelle et verrous UI.
- Observabilite: Sentry (browser), Web Vitals vers /api/v1/metrics/frontend (optionnel), feature flags client.
- Domaines: auth (login/refresh/roles), dashboard, planning (jour/semaine/mois) avec drag and drop, missions, techniciens, disponibilites, notifications, exports (CSV/PDF/ICS), settings org, analytics.

---

## 2) Principes de design
- Separation des responsabilites: composants presentatifs vs containers/hook.
- Data fetching: React Query (staleTime, cacheTime, background refetch), invalidations precises par cle.
- Types: generation automatique depuis OpenAPI backend via openapi-typescript. Aucun any.
- Routing: React Router v6, nested routes, lazy loading avec Suspense + Skeleton.
- DnD: dnd-kit pour planning, contraintes d’accessibilite (drag via clavier), annulation avec ESC.
- i18n: architecture prete (en-US par defaut), francais actif, extraction de messages centralisee.
- Theming: design tokens Tailwind CSS variables (HSL), dark/light, density mode (compact/comfortable).
- UX: toasts non bloquants, confirmations claires, autosave ou draft state pour formulaires longs.

---

## 3) Arborescence de reference
```
src/
  api/
    client.ts          # ky ou axios avec interceptors JWT + retry
    openapi-types.ts   # genere (ne pas editer)
    endpoints.ts       # wrappers type-safe
  app/
    routes.tsx         # definition des routes lazy
    providers.tsx      # QueryClientProvider, ThemeProvider, ErrorBoundary
    error-boundary.tsx
  components/
    ui/                # atoms shadcn/base
    layout/            # AppShell, Navbar, Sidebar, Breadcrumbs
    feedback/          # Toast, Alert, EmptyState
    data/              # DataTable, Pagination, Filters
    forms/             # inputs RHF + zod resolver
    planning/          # CalendarGrid, EventCard, DnDHandles
  features/
    auth/
      pages/           # Login, Logout, Callback
      hooks/           # useAuth, useSession
      store/
    missions/
      pages/
      components/
      hooks/
    planning/
      pages/
      hooks/
  hooks/
    useTheme.ts
    useHotkeys.ts
  lib/
    utils.ts
    tz.ts
  pages/
    dashboard.tsx
    settings.tsx
  store/
    auth.ts           # Zustand slice
    settings.ts       # theme, density
  styles/
    globals.css
    tailwind.css
  tests/
    unit/
    e2e/
  main.tsx
  App.tsx
```

---

## 4) Environnements et .env.example
```
VITE_API_URL=http://localhost:8000/api/v1
VITE_APP_ENV=dev
VITE_SENTRY_DSN=
VITE_FEATURE_FLAGS=
VITE_PUBLIC_URL=http://localhost:5173
```

- Variables uniquement prefixees VITE_. Jamais de secrets reels en frontend.

---

## 5) Client API et contrats
### 5.1 Client HTTP
```ts
// src/api/client.ts
import ky from "ky";
export const api = ky.create({
  prefixUrl: import.meta.env.VITE_API_URL,
  hooks: { beforeRequest: [authHeader], afterResponse: [handle401] },
  timeout: 15000,
});
```

### 5.2 Types OpenAPI
- Generation: `pnpm dlx openapi-typescript http://localhost:8000/openapi.json -o src/api/openapi-types.ts`
- Politique: un job CI verifie que `openapi-types.ts` est synchro (hash sur schema).

### 5.3 Wrappers endpoint
```ts
// src/api/endpoints.ts
import { api } from "./client";
import { paths } from "./openapi-types";
export type Mission = paths["/missions"]["get"]["responses"][200]["content"]["application/json"]["items"][number];
export async function listMissions() {
  return api.get("missions").json<{ items: Mission[] }>();
}
```

---

## 6) State management
- React Query: lecture/ecriture vers API, invalidation par scope (missions, planning:day:YYYY-MM-DD, planning:week:ISOweek).
- Zustand: auth/session (tokens memoire), UI prefs (theme, density), feature flags.
- Pas de store global pour les listes volumineuses si React Query suffit.

---

## 7) Routing protege
```tsx
// src/app/routes.tsx
import { createBrowserRouter } from "react-router-dom";
import { Protected } from "./protected";
export const router = createBrowserRouter([
  { path: "/login", lazy: () => import("@/features/auth/pages/login") },
  { element: <Protected />, children: [
      { path: "/", lazy: () => import("@/pages/dashboard") },
      { path: "/planning", lazy: () => import("@/features/planning/pages/planning") },
      { path: "/missions", lazy: () => import("@/features/missions/pages/missions") },
      { path: "/settings", lazy: () => import("@/pages/settings") },
  ]},
]);
```

```tsx
// src/app/protected.tsx
import { Navigate, Outlet } from "react-router-dom";
import { useAuth } from "@/store/auth";
export function Protected() {
  const { isAuthenticated } = useAuth();
  return isAuthenticated ? <Outlet /> : <Navigate to="/login" replace />;
}
```

---

## 8) Planning et Drag & Drop (accessibilite incluse)
- DnD via dnd-kit: keyboard sensors, pointer sensors, collision detection.
- Snapping sur grille de 5 minutes, contraintes de chevauchement visuelles.
- Undo/Redo local avec history en memoire, sauvegarde optimiste vers API.
- A11y: handles focusables, role="button", aria-grabbed, aria-dropeffect.

```tsx
// src/components/planning/EventCard.tsx
export function EventCard(props:{title:string,start:Date,end:Date,onDragEnd:(next:{start:Date,end:Date})=>void}){ /* ... */ }
```

---

## 9) Accessibilite
- axe-core en tests unitaires Storybook et e2e Playwright.
- Focus visible, skip links, gestion du tab-order.
- Composants Radix preconises (dialog, popover, select) pour a11y solide.

---

## 10) Performance
- Split par route, React.lazy, prefetch sur survol nav.
- Reselect memo pour listes; virtualization si > 200 elements.
- Images: formats modernes, dimensions fixes, lazy.
- Cache HTTP: etags/304 cote backend; SW optionnel pour offline light.

---

## 11) Observabilite
- Sentry: captureException, sourcemaps uploads en CI (optionnel).
- Web Vitals: envoi LCP/CLS/INP a /api/v1/metrics/frontend (si expose).
- Feature flags: simple map dans Zustand, overridable via localStorage.

---

## 12) Scripts PowerShell (Windows-first)
```
# tools/dev/dev_front.ps1
param([switch]$Clean)
$ErrorActionPreference = "Stop"
if ($Clean) { if (Test-Path node_modules) { Remove-Item node_modules -Recurse -Force } }
pnpm install --frozen-lockfile
pnpm dev

# tools/dev/test_front.ps1
$ErrorActionPreference = "Stop"
pnpm test -- --coverage

# tools/dev/e2e_front.ps1
$ErrorActionPreference = "Stop"
pnpm exec playwright install --with-deps
pnpm exec playwright test
```

---

## 13) ESLint, TSConfig, Tailwind (extraits)
```json
// package.json (scripts)
{
  "scripts": {
    "dev": "vite",
    "build": "tsc -b && vite build",
    "preview": "vite preview",
    "lint": "eslint .",
    "typecheck": "tsc --noEmit",
    "test": "vitest",
    "storybook": "storybook dev -p 6006",
    "build-storybook": "storybook build"
  }
}
```

```json
// tsconfig.json (extrait)
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "ESNext",
    "jsx": "react-jsx",
    "baseUrl": ".",
    "paths": { "@/*": ["src/*"] },
    "strict": true,
    "noUncheckedIndexedAccess": true,
    "exactOptionalPropertyTypes": true
  }
}
```

```js
// .eslintrc.cjs (extrait)
module.exports = {
  root: true,
  parser: "@typescript-eslint/parser",
  plugins: ["@typescript-eslint", "react", "react-hooks", "jsx-a11y"],
  extends: [
    "eslint:recommended",
    "plugin:@typescript-eslint/recommended",
    "plugin:react/recommended",
    "plugin:react-hooks/recommended",
    "plugin:jsx-a11y/recommended"
  ],
};
```

---

## 14) Storybook et Chromatic
- Storybook 8: stories par composant, docs MDX, controls.
- Guard storybook_guard.ps1: build obligatoire sur PR.
- Chromatic: verrous visuels; si indisponible, fallback sur capture Playwright snapshots.

```yml
# .github/workflows/storybook.yml
name: Codex CI / storybook
on: [pull_request]
jobs:
  build:
    runs-on: ubuntu-24.04
    steps:
      - uses: actions/checkout@v4
      - uses: pnpm/action-setup@v4
        with: { version: 9 }
      - run: pnpm install --frozen-lockfile
      - run: pnpm build-storybook
```

---

## 15) Lighthouse CI (optionnel mais recommande)
```yml
# .github/workflows/lighthouse.yml
name: Codex CI / lighthouse
on: [pull_request]
jobs:
  lhci:
    runs-on: ubuntu-24.04
    steps:
      - uses: actions/checkout@v4
      - uses: pnpm/action-setup@v4
        with: { version: 9 }
      - run: pnpm install --frozen-lockfile
      - run: pnpm build
      - run: npx http-server dist -p 4173 &
      - run: npx @lhci/cli autorun --upload.target=temporary-public-storage
```

- Gate: echec si score < 90 (configurable).

---

## 16) Workflows CI front (durcis)
```yml
# .github/workflows/frontend-tests.yml
name: Codex CI / frontend-tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-24.04
    steps:
      - uses: actions/checkout@v4
      - uses: pnpm/action-setup@v4
        with: { version: 9 }
      - name: Install deps
        run: pnpm install --frozen-lockfile
      - name: Lint + typecheck
        run: pnpm lint && pnpm typecheck
      - name: Unit tests
        run: pnpm test -- --coverage --run
      - name: Coverage gate >= 70%
        run: |
          node -e "const fs=require('fs');const s=JSON.parse(fs.readFileSync('coverage/coverage-summary.json'));const c=s.total.lines.pct;console.log('Coverage',c);process.exit(c>=70?0:1)"
      - name: E2E tests
        run: pnpm exec playwright test
```

---

## 17) Guards et integration Hub
- `roadmap_guard.ps1`: exige `Ref: docs/roadmap/step-XX.md` dans PR/dernier commit.
- `commit_guard.ps1`: verifie `docs/codex/last_output.json` si present.
- `storybook_guard.ps1`: verifie le build Storybook.
- Tous appeles par `tools/guards/run_all_guards.ps1` utilise en CI `Codex CI / guards`.

```ps1
# tools/guards/run_all_guards.ps1 (extrait)
$ErrorActionPreference = "Stop"
& pwsh -File tools/guards/roadmap_guard.ps1 --strict
& pwsh -File tools/guards/commit_guard.ps1 --strict
& pwsh -File tools/guards/storybook_guard.ps1
```

---

## 18) PR template et checklists
```md
## Summary
- ...

## Testing
- unitaires: ...
- e2e: ...
- storybook: ...
- lighthouse: ...

- [ ] Lint + typecheck OK
- [ ] Tests unitaires OK (coverage >= 70 %)
- [ ] Tests e2e OK
- [ ] Lighthouse >= 90
- [ ] 0 erreurs a11y critiques

Ref: docs/roadmap/step-XX.md
```

---

## 19) Runbooks incidents
- Build echoue: supprimer node_modules et lockfile, pnpm install; si Vite plugin en cause, desactiver temporairement et ouvrir issue.
- Cypress/Playwright flakys: augmenter timeouts, stabiliser selectors data-test-id, desactiver animations via prefers-reduced-motion en e2e.
- Regressions UI: verifier Chromatic, revalider snapshots e2e si legitimes.
- Lighthouse < 90: analyser traces, activer code-splitting plus agressif, retirer dependances lourdes.
- A11y erreurs: corriger roles/labels, valider au clavier, ajouter aria-live pour toasts.

---

## 20) Acceptation et KPIs
- Gate CI: Lint OK, Typecheck OK, Unit >= 70 %, E2E OK, Storybook build OK, Lighthouse >= 90, 0 axe critical.
- Perf: P95 interaction < 200 ms cote UI (hors reseau), FPS ~60 sur scroll listes.
- SLO UI: 99 % pages chargees sans erreur front fatale par semaine.

---

## 21) Prompts Codex prets-a-coller
```md
PROMPT.frontend.step-N.md
SYSTEM
Tu es Codex Frontend. Tu produis du code React/TS ASCII only, teste et deterministe. Tu dois faire passer lint, typecheck, tests (coverage >= 70 %), e2e, Storybook build, Lighthouse >= 90. Ajoute la ligne Ref dans le commit/PR.

USER
Contexte: <scope exact de l’etape N>
Attendus:
- code sous src/... (liste)
- stories .stories.tsx + docs MDX
- tests vitest + playwright
- mise a jour README si necessaire
CI/GUARDS:
- run ./tools/guards/run_all_guards.ps1
- coverage >= 70 %, Lighthouse >= 90
Commit:
chore(step-N): <resume>
Ref: docs/roadmap/step-N.md

ACCEPTANCE
- Lint/Tests OK, coverage >= 70 %
- Storybook a jour
- Lighthouse >= 90
- 0 erreurs a11y critiques
```

```md
PROMPT.frontend.fix-guards.md
SYSTEM
Tu es Codex Frontend. Corrige les guards/CI (lint, typecheck, storybook, coverage, lighthouse) sans degrader la qualite.

USER
Logs: <coller logs>
Actions:
- patch tools/guards/*.ps1
- patch .github/workflows/*.yml
- si Ref manquant: commit vide + push (fallback SSH->HTTPS)
Commit:
chore(ci): fix frontend guards to unblock PR
Ref: docs/roadmap/step-XX.md
```

---

## 22) Roadmap Frontend (20 etapes, sous-steps X.Y si CI KO)
1. Scaffold Vite + TS + Tailwind + shadcn/ui + ESLint/Prettier
2. Router + ProtectedRoute + providers de base
3. Auth pages + Zustand auth + interceptors
4. AppShell + dashboard widgets skeleton
5. Planning jour avec DnD (base) + sources mock
6. Planning semaine + bind API /planning/day|week
7. Missions CRUD UI + tables filtrables
8. Techniciens CRUD UI + avatars placeholders
9. Disponibilites overlay calendrier + conflits basiques
10. Notifications UI (toasts, center)
11. Exports (CSV, PDF) front triggers
12. ICS export/import UI
13. Analytics (recharts) + cartes KPI
14. Storybook complet + Chromatic
15. A11y pass (axe, keyboard-only)
16. Theming complet (dark/light, density)
17. Multi-tenant (branding basic)
18. Optimisations perf (code split, images, memo)
19. CI hardening (lhci, chromatic strict)
20. Stabilisation LTS + docs definitives

---

## 23) Exemples de composants et patterns
### 23.1 DataTable minimal
```tsx
// src/components/data/DataTable.tsx
export function DataTable<T>({rows, columns}:{rows:T[];columns:{key:keyof T;label:string}[]}){ /* ... */ }
```

### 23.2 Form pattern RHF + Zod
```ts
// src/components/forms/schemas.ts
import { z } from "zod";
export const missionSchema = z.object({ title: z.string().min(2), start_at: z.string(), end_at: z.string() });
```

### 23.3 Toast service
```ts
// src/components/feedback/toast.ts
export const toast = { success:(m:string)=>{/*...*/}, error:(m:string)=>{/*...*/} };
```

---

## 24) Politiques et conventions
- Commits: Conventional Commits, scope frontend.
- Nommage fichiers: kebab-case pour fichiers, PascalCase pour composants.
- Alias imports: @/ vers src/ obligatoire.
- No default export pour composants complexes (preferer nommes).
- Donnees de test: fixtures deterministes.

---

## 25) Integration Backend et contrats
- Les endpoints critiques doivent avoir des mocks MSW pour tests offline.
- Les schemas Zod refleteront la validation UI (complementaires aux schemas backend).
- Tout changement de contrat: PR conjointe avec backend + mise a jour openapi-types.ts.

---

## 26) Annexes pratiques
- VSCode settings recommandees: formatOnSave, path intellisense, eslint.
- Matrice compat: Node 20+, PNPM 9+, Ubuntu 24.04 runner, Windows 11.
- Export build: `pnpm build` produit `dist/` pret pour Caddy/NGINX.

---

## 27) Acceptation finale
- Documenter dans docs/roadmap/step-XX.md les changements UI et captures.
- Ajouter Ref obligatoire dans PR/commit.
- Si echec CI: creer step-XX.1.md expliquant patch minimal, recommencer jusqu’a vert.

Fin. 

