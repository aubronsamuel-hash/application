# AGENT.md (Hub principal du Codex)

## 1. Introduction

Bienvenue dans le **Codex des Agents**.  
Ce fichier `AGENT.md`, placé à la racine du projet, est le **point d’entrée central, l’index global et la référence absolue** pour Codex et pour les contributeurs humains.  

### 1.1 Philosophie
- **Un agent = une spécialisation** : chaque agent couvre un domaine clairement défini (backend, frontend, devops, docs).  
- **Le hub = cerveau central** : ce fichier relie tout, fixe les règles et impose les conventions communes.  
- **Lecture séquentielle** : Codex commence toujours par `AGENT.md` puis explore les sous-agents et la roadmap.

### 1.2 Objectifs
- Centraliser la **connaissance** et les **règles de travail**.  
- Garantir la **cohérence documentaire et technique**.  
- Synchroniser les sous-agents avec la **roadmap (20 étapes principales + correctifs)** et avec la **CI/CD**.  
- Assurer la **traçabilité** de toutes les décisions et évolutions.  
- Documenter et gérer les **sous-steps correctifs** (`step-XX.1`, `step-XX.2`) si une CI ou un test échoue.

---

## 2. Architecture des agents

### 2.1 Structure des fichiers

```
/AGENT.md                        <- hub principal
/docs/agents/AGENT.backend.md    <- logique serveur (API, DB, auth)
/docs/agents/AGENT.frontend.md   <- interface utilisateur (UI, state)
/docs/agents/AGENT.devops.md     <- CI/CD, infra, monitoring
/docs/agents/AGENT.docs.md       <- roadmap, guards, policies
/docs/roadmap/step-01.md         <- étape principale
/docs/roadmap/step-01.1.md       <- correctif si échec de step 01
...
/docs/roadmap/step-20.md         <- étape finale
```

### 2.2 Diagramme conceptuel

```
                  +------------------+
                  |     AGENT.md     |
                  | (hub principal)  |
                  +--------+---------+
                           |
     -------------------------------------------------
     |                   |                   |       |
+----+-----+       +-----+-----+       +-----+--+ +--+----+
| Backend  |       | Frontend  |       | DevOps | | Docs  |
| Agent    |       | Agent     |       | Agent  | | Agent |
+----------+       +-----------+       +--------+ +-------+
                           |
                    +------+------+
                    |   Roadmap   |
                    | (steps &    |
                    | corrections)|
                    +-------------+
```

### 2.3 Relations croisées
- **Backend ↔ Frontend** : API contracts, types partagés.  
- **Backend ↔ DevOps** : DB, migrations, déploiements.  
- **Frontend ↔ Docs** : UI guidelines, policies.  
- **DevOps ↔ Docs** : CI/CD, guards, sécurité.  

### 2.4 Principes directeurs
- **Modularité** : chaque agent doit être indépendant.  
- **Interopérabilité** : collaboration via contrats documentés.  
- **Traçabilité** : chaque changement justifié dans la roadmap.  
- **Reproductibilité** : valide sous Windows (PowerShell) et CI Linux.  
- **Correctivité** : sous-step créé dès qu’un test ou CI échoue.  

---

## 3. Détail des agents

### 3.1 Backend (`docs/agents/AGENT.backend.md`)
- **Mission** : logique applicative, persistance et APIs.  
- **Fonctions clés** : FastAPI, SQLAlchemy, Alembic, RBAC, services internes, tests, export OpenAPI.  
- **Interactions** :
  - avec **Frontend** via API contracts,  
  - avec **DevOps** pour migrations et déploiement.  
- **KPIs** : couverture > 80 %, temps de réponse < 200ms.  
- **Lien** : [AGENT.backend.md](docs/agents/AGENT.backend.md)

### 3.2 Frontend (`docs/agents/AGENT.frontend.md`)
- **Mission** : fournir une UI performante et accessible.  
- **Fonctions clés** : React, Tailwind, shadcn/ui, routing sécurisé, Storybook, Chromatic, Vitest, Playwright, a11y.  
- **Interactions** :
  - avec **Backend** via appels API,  
  - avec **Docs** pour UI guidelines.  
- **KPIs** : Lighthouse > 90, 0 erreurs a11y critiques.  
- **Lien** : [AGENT.frontend.md](docs/agents/AGENT.frontend.md)

### 3.3 DevOps (`docs/agents/AGENT.devops.md`)
- **Mission** : déploiement, CI/CD, sécurité et observabilité.  
- **Fonctions clés** : GitHub Actions, Docker, Caddy, Prometheus, Grafana, Loki, audits de dépendances, k6.  
- **Interactions** :
  - avec **Backend** (DB, API infra),  
  - avec **Docs** (guards, pipelines).  
- **KPIs** : CI verte en < 5 min, infra redéployable en 1 commande.  
- **Lien** : [AGENT.devops.md](docs/agents/AGENT.devops.md)

### 3.4 Documentation (`docs/agents/AGENT.docs.md`)
- **Mission** : gouvernance documentaire et roadmap.  
- **Fonctions clés** : roadmap, guards, policies, génération auto (Codex prompts, last_output.json).  
- **Interactions** : avec tous les agents.  
- **KPIs** : 100 % commits référencés, CI docs_guard sans fail.  
- **Lien** : [AGENT.docs.md](docs/agents/AGENT.docs.md)

---

## 4. Mode d’utilisation

### 4.1 Ordre de lecture
1. Commencer par `AGENT.md`.  
2. Naviguer vers l’agent concerné.  
3. Lire `docs/roadmap/step-XX.md`.  
4. Si échec de CI/tests → créer et documenter `step-XX.1.md`, puis `step-XX.2.md` si besoin.  

### 4.2 Codex (IA)
- **Point de départ** : `AGENT.md`.  
- **Navigation** : seulement via liens définis.  
- **Obligation** : appliquer conventions/guards.  
- **Réaction en cas d’échec** : générer sous-step documenté.  

### 4.3 Règles de navigation
- Backend ↔ Frontend : contrats API et modèles.  
- Backend ↔ DevOps : secrets, migrations, déploiements.  
- Frontend ↔ Docs : cohérence UI.  
- DevOps ↔ Docs : conformité CI/CD.  

---

## 5. Gouvernance & conventions

### 5.1 Rédaction
- ASCII only.  
- Markdown strict.  
- Pas de TODO non résolu.  

### 5.2 Validation
- Steps = `docs/roadmap/step-XX.md`.  
- Correctifs = `docs/roadmap/step-XX.1.md`, `step-XX.2.md`, etc.  
- Validation requise :
  ```
  VALIDATE? yes/no
  ```

### 5.3 Référencement obligatoire
```
Ref: docs/roadmap/step-XX.md
```

### 5.4 Mise à jour
- Nouvel agent → `/docs/agents/`.  
- `AGENT.md` MAJ immédiate.  
- Guards bloquent incohérences.  

### 5.5 Contrats qualité
- Backend : tests > 80 %, docs API sync.  
- Frontend : Lighthouse > 90, pas d’erreurs critiques.  
- DevOps : CI < 5min, déploiement reproductible.  
- Docs : couverture 100 %.  

---

## 6. Roadmap & versioning

- Roadmap = **20 étapes principales** (`step-01.md` → `step-20.md`).  
- Chaque étape peut avoir des **sous-steps correctifs** (`step-01.1.md`, `step-01.2.md`).  
- Nouvelle version taggée tous les 5 steps validés.  
- Change log obligatoire à chaque release.  

**Version actuelle : v0.1 (draft).**

---

## 7. Annexes

### 7.1 Glossaire
- **Agent** : spécialisation autonome.  
- **Guard** : script PowerShell validateur CI.  
- **Codex** : AGENT.md + sous-agents + roadmap.  
- **Step** : étape principale validée.  
- **Sub-step** : correctif lié à un step.  

### 7.2 Inspirations
- Skello, Combo, EventSoft.  
- Pipelines modernes (GitHub Actions, GitLab).  
- Docs strictes (Rust RFCs, Kubernetes KEPs).  

### 7.3 Schémas futurs
- Endpoints API.  
- Pipelines CI/CD.  
- Architecture Docker Compose.  
- Organigrammes guards.  

### 7.4 Bonnes pratiques
- **DRY** : pas de duplication.  
- **KISS** : simplicité maximale.  
- **Fail fast** : guards bloquent tôt.  
- **Auditabilité** : tout commit traçable via `Ref:`.  
- **Correctivité** : sous-steps obligatoires en cas d’échec.  

---

# ✅ Résumé

- `AGENT.md` = hub absolu.  
- Les sous-agents couvrent chacun leur domaine.  
- La roadmap = 20 étapes + sous-steps correctifs.  
- Les guards garantissent discipline et conformité.  
- Codex commence ici et respecte strictement ces règles.

