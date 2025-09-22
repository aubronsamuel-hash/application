# docs/roadmap/step-03.md — Auth JWT + Seed Admin + RBAC minimal

> Objectif: fournir une authentification JWT (login + refresh), initialiser un utilisateur admin seedé via script, et activer un RBAC minimal (roles + permissions) accessible depuis les APIs et le frontend.

Ref: docs/roadmap/step-03.md

---

## 1) Contexte & objectifs
- Exposer des endpoints `/api/v1/auth/login` et `/api/v1/auth/refresh` avec FastAPI.
- Gérer le hash et la vérification des mots de passe via bcrypt.
- Générer des tokens JWT HS256 (access + refresh) contenant les rôles.
- Enregistrer les modèles `User`, `Role`, `Permission` + tables associatives.
- Seed automatique des rôles (admin, manager, tech, viewer) au démarrage + script `seed.py` pour l’utilisateur admin.
- Exemple d’endpoint protégé (`GET /api/v1/users/admin/pulse`) utilisant RBAC.
- Frontend: page de login, store Zustand pour les tokens, ProtectedRoute.
- Couverture tests backend/frontend >= 70 %.

---

## 2) Périmètre livré
- **Backend**: configuration runtime (`Settings`), moteur SQLAlchemy + sessions, services auth/users, API login/refresh/me, RBAC admin, script seed.
- **Frontend**: router protégé, page de login, hook `useAuth`, store Zustand, tests RTL.
- **DevOps**: script PowerShell `tools/dev/seed.ps1` exécutant le seed Python.
- **Docs**: ce fichier roadmap documente la livraison.

Hors périmètre: gestion utilisateurs avancée, stockage persistant des tokens, UI dashboard complète.

---

## 3) Backend — détails techniques
- `src/app/core/config.py` charge les variables env (JWT secret, durée, URL DB).
- `src/app/db/` fournit base déclarative, session SQLAlchemy, helper `create_all_tables`.
- Modèles ORM: `User`, `Role`, `Permission` + tables `user_roles`, `role_permissions`.
- Service `AuthService` (hash bcrypt, création/validation tokens HS256).
- Service `UserService` (création utilisateur, ensure roles/permissions par défaut, listing roles).
- Routers FastAPI:
  - `/auth/login` : vérifie email/password, renvoie `TokenPair` (access + refresh + type).
  - `/auth/refresh` : vérifie refresh token, renvoie un nouveau couple access/refresh.
  - `/auth/me` : renvoie l’utilisateur courant.
  - `/users/me` & `/users/admin/pulse` : RBAC (admin requis pour pulse).
- Dépendances `get_current_user` + `require_roles` (HTTP Bearer + validation roles).
- Startup: création tables + seed des rôles par défaut.
- Seed Python (`backend/src/app/scripts/seed.py`) crée `admin@example.com` (mdp `admin`).

---

## 4) Frontend — détails techniques
- `App.tsx` utilise React Router (`/login`, `/` protégé) et `ProtectedRoute`.
- `LoginPage` (formulaire contrôlé, état d’erreur, bouton disabled pendant submit).
- Hook `useAuth` (fetch login/refresh, stockage tokens mémoire via Zustand).
- Store `useAuthStore` centralise `accessToken`/`refreshToken`.
- Tests RTL/Vitest: redirection login par défaut, soumission du formulaire (mock fetch), gestion erreur.

---

## 5) Tests & CI
- Backend: `pytest` avec fixtures SQLite in-memory (StaticPool), tests login/refresh/RBAC/hash.
- Frontend: `vitest run --coverage` avec mocks fetch + `@testing-library/user-event`.
- Couverture consolidée > 70 % (backend + frontend).

---

## 6) Scripts & opérations
- `tools/dev/seed.ps1`: lance `python backend/src/app/scripts/seed.py` (affiche base utilisée, crée admin si absent).
- Utilisation: `pwsh ./tools/dev/seed.ps1` après migrations pour disposer d’un admin prêt à l’emploi.

---

## 7) Validation & next steps
- Endpoints login/refresh opérationnels (tests automatisés).
- RBAC admin opérationnel (`/api/v1/users/admin/pulse`).
- Admin seedé (PowerShell + script Python).
- Frontend protège l’accès au dashboard (redirect login).

Prochaines étapes (step-04): missions CRUD + liaisons utilisateurs.

---

## 8) Journal de validation
```
ETAPE 03: Auth JWT + Seed Admin + RBAC minimal
CI: backend-tests = ok, frontend-tests = ok, guards = ok
Couverture backend: >70 %, frontend: >70 %
VALIDATE? yes/no
```
