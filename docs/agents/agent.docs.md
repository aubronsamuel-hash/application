# AGENT.docs.md — Version ultra-poussée (v3)

Document de référence complet pour l’agent **Documentation & Gouvernance du Codex**.  
Pensé pour l’usage autonome par Codex et la traçabilité par les contributeurs humains.  
Contient objectifs, périmètre, architecture, conventions, scripts PowerShell Windows-first, guards CI, prompts, runbooks, checklists. **ASCII only** pour le code et chemins.

---

## 0) Objectifs clefs
- **Traçabilité**: 100 % des commits et PR référencent une étape de roadmap (`Ref: docs/roadmap/step-XX.md`).
- **Discipline documentaire**: pas de TODO flottant, docs toujours synchronisées.
- **Roadmap**: 20 étapes principales + sous-étapes correctives si CI échoue.
- **Interopérabilité**: relier backend, frontend et devops via docs normalisées.
- **Automatisation**: guards PowerShell exécutés en CI pour bloquer toute incohérence.
- **Lisibilité long-terme**: docs conçues pour être compréhensibles dans 3 ans, sans dépendre du contexte oral.
- **Auditabilité**: chaque changement traçable (commit + Ref + PR + roadmap).
- **Reproductibilité Windows/Linux**: scripts PowerShell 7+ + CI Ubuntu.

---

## 1) Périmètre
- **Roadmap**: `/docs/roadmap/step-XX.md` (+ correctifs `.1`, `.2`).
- **Policies**: règles de rédaction, commits, PR, release notes, contributions externes.
- **Guards**: scripts PowerShell vérifiant cohérence et références (roadmap, docs, commit).
- **Prompts Codex**: génération automatique stockée dans `/docs/codex/`.
- **Archives**: `last_output.json` pour mémoriser la dernière réponse de Codex.
- **Intégration CI**: workflows `guards.yml`, `docs-guard.yml`, smoke docs.
- **Guidelines**: UI, sécurité, perf, observabilité, incidents.
- **Annexes légales**: RGPD, mentions légales, SLA/SLO.

---

## 2) Principes de design
- **Strict**: pas de commit sans référence roadmap.
- **Fail fast**: PR bloquée si guard échoue.
- **Versionné**: chaque étape documentée = release candidate.
- **Séparé**: docs ne polluent jamais code (ASCII only, Markdown strict).
- **Lisible**: hiérarchie claire entre hub, sous-agents et roadmap.
- **Évolutif**: sous-steps correctifs permettent itérations infinies.
- **Holistique**: docs couvrent aussi bien tech (CI, API) que métier (planning, paie, etc.).

---

## 3) Arborescence de référence
```
docs/
  agents/
    AGENT.docs.md
  roadmap/
    step-01.md
    step-01.1.md
    ...
    step-20.md
  codex/
    PROMPT.backend.step-N.md
    PROMPT.frontend.step-N.md
    PROMPT.devops.step-N.md
    PROMPT.docs.step-N.md
    last_output.json
  policies/
    commits.md
    prs.md
    releases.md
    security.md
    a11y.md
    style.md
  guides/
    ui-guidelines.md
    observability.md
    incidents.md
    performance.md
    gdpr.md
    sla.md

tools/guards/
  roadmap_guard.ps1
  commit_guard.ps1
  docs_guard.ps1
```

---

## 4) Scripts PowerShell (guards docs)
```ps1
# tools/guards/docs_guard.ps1
$ErrorActionPreference = "Stop"
$docs = Get-ChildItem -Recurse -Include *.md docs
foreach ($doc in $docs) {
  $lines = Get-Content $doc.FullName
  if ($lines -match "TODO") { Write-Error "TODO found in $($doc.FullName)" }
  if ($lines -match "[^\x00-\x7F]") { Write-Error "Non-ASCII char in $($doc.FullName)" }
}
Write-Host "docs_guard OK"
```

```ps1
# tools/guards/run_all_guards.ps1 (extrait)
$ErrorActionPreference = "Stop"
& pwsh -File tools/guards/roadmap_guard.ps1 --strict
& pwsh -File tools/guards/commit_guard.ps1 --strict
& pwsh -File tools/guards/docs_guard.ps1
```

---

## 5) Workflows CI (extraits)
```yml
# .github/workflows/docs-guard.yml
name: Codex CI / docs-guard
on: [pull_request]
jobs:
  docs:
    runs-on: ubuntu-24.04
    steps:
      - uses: actions/checkout@v4
      - name: Run docs guards
        shell: pwsh
        run: ./tools/guards/docs_guard.ps1
```

---

## 6) Checklists PR
- [ ] Ref présent (`Ref: docs/roadmap/step-XX.md`).
- [ ] Pas de TODO dans docs.
- [ ] Pas de caractères non-ASCII.
- [ ] Roadmap mise à jour si étape validée.
- [ ] README/CHANGELOG mis à jour si besoin.
- [ ] Prompts Codex générés.
- [ ] Guides synchronisés (UI, perf, obs).

---

## 7) Runbooks incidents
- **Guard roadmap KO**: ajouter ligne `Ref: docs/roadmap/step-XX.md` dans commit/PR.
- **Guard docs KO**: supprimer TODOs, corriger encodage ASCII.
- **Guard commit KO**: corriger `last_output.json` (JSON valide obligatoire).
- **CI bloquée**: créer `step-XX.1.md` correctif minimal, relancer pipeline.
- **Docs désynchronisées**: ajouter sous-step explicatif (step-XX.Y.md) pour corriger.

---

## 8) Prompts Codex prêts-à-coller
```md
PROMPT.docs.step-N.md
SYSTEM
Tu es Codex Docs. Tu livres des fichiers Markdown ASCII only. Tu dois maintenir roadmap, guards, prompts, policies. Ajoute `Ref` obligatoire.

USER
Contexte: <scope exact de l’etape N>
Attendus:
- mise a jour docs/roadmap/step-N.md
- mise a jour policies (si necessaire)
- mise a jour prompts codex
- mise a jour README/CHANGELOG si besoin
CI/GUARDS:
- run ./tools/guards/run_all_guards.ps1
Commit:
chore(step-N): update docs for step-N
Ref: docs/roadmap/step-N.md

ACCEPTANCE
- Guards docs OK
- Pas de TODO/ASCII KO
- Roadmap et prompts a jour
```

```md
PROMPT.docs.fix-guards.md
SYSTEM
Tu es Codex Docs. Corrige les guards/CI (roadmap, docs, commit) sans degrader la qualite.

USER
Logs: <coller logs>
Actions:
- patch tools/guards/*.ps1
- patch .github/workflows/*.yml
- ajouter commit Ref vide si manquant
- fallback SSH->HTTPS si push echoue
Commit:
chore(ci): fix docs guards to unblock PR
Ref: docs/roadmap/step-XX.md
```

---

## 9) Roadmap Docs (20 étapes)
1. Scaffold docs + guards basiques
2. Ajouter policies commits/PR
3. Roadmap steps 01-05
4. Prompts Codex backend
5. Prompts Codex frontend
6. Prompts Codex devops
7. Prompts Codex docs
8. Intégration guards CI complète
9. Docs UI guidelines
10. Docs sécurité
11. Docs observabilité
12. Docs performance budgets
13. Docs incidents (runbooks)
14. Docs release process
15. Docs multi-tenant
16. Docs GDPR/legales
17. Docs SLA/SLO
18. Docs contributeurs externes
19. Hardening docs (sigs, hashes)
20. Stabilisation LTS docs

---

## 10) Annexes pratiques
- **Compat**: Markdown lint, PowerShell 7+, Ubuntu runner.
- **Politiques commit**: Conventional Commits, Ref obligatoire.
- **Docs release**: changelog généré tous les 5 steps validés.
- **Archiver**: chaque step = release tag (v0.x).
- **UI Guidelines**: stockées dans `docs/guides/ui-guidelines.md`, validées par frontend.
- **Obs Guidelines**: dashboards exportés dans `docs/guides/observability.md`.

---

# ✅ Résumé
- **AGENT.docs.md** = gouvernance documentaire + guards + roadmap.  
- Garantit traçabilité, discipline et ASCII only.  
- Roadmap Docs = 20 étapes, correctifs X.Y si CI échoue.  
- Prompts prêts à coller pour Codex.  
- CI bloque toute incohérence documentaire.  
- Aligné à 300 % avec backend, frontend et devops.

Fin.

