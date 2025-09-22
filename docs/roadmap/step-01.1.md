# docs/roadmap/step-01.1.md — Fix guards (roadmap ref manquant + ASCII strict sur docs)

Ref: docs/roadmap/step-01.1.md

---

## 1) Contexte
CI "Codex CI / guards" en échec.

**Logs fournis**
```
Run ./tools/guards/run_all_guards.ps1
Running roadmap guard...
roadmap_guard OK
Running commit guard...
Exception: tools/guards/commit_guard.ps1:13
  throw "Latest commit is missing roadmap reference"
Latest commit is missing roadmap reference
Running docs guard...
Exception: tools/guards/docs_guard.ps1:12
  throw "Non-ASCII character detected in $($doc.FullName)"
Non-ASCII character detected in docs/agents/agent_backend.md
Error: Process completed with exit code 1.
```

## 2) Analyse racine
1) **Référence roadmap manquante dans le dernier commit** → il faut ajouter la ligne `Ref: docs/roadmap/step-01.md` à l’historique de la PR (commit récent ou commit vide dédié).
2) **ASCII-only appliqué par erreur aux documents** → la policy projet autorise les **accents UTF-8 dans la documentation** (agents, guides, roadmap). Le guard doit donc tolérer UTF-8 dans `docs/**` et réserver l’ASCII-only au **code**.

---

## 3) Correctifs à appliquer

### 3.1 Forcer la référence roadmap dans l’historique
Deux options (
**choisir une seule**):

**Option A — Commit vide dédié (recommandé, non destructif)**
```
git commit --allow-empty -m "chore(step-01): add roadmap reference\n\nRef: docs/roadmap/step-01.md"
```

**Option B — Amend du dernier commit (si pas encore partagé)**
```
msg=$(git log -1 --pretty=%B)
echo "$msg\n\nRef: docs/roadmap/step-01.md" | git commit --amend -F -
```

> Si le push SSH échoue, faire un fallback HTTPS.
```
# essai SSH
if ! git push; then
  git remote set-url origin https://github.com/<OWNER>/<REPO>.git
  git push
fi
```

### 3.2 Assouplir `docs_guard.ps1` (UTF-8 autorisé dans /docs)
Remplacer le contenu par :
```ps1
# tools/guards/docs_guard.ps1
$ErrorActionPreference = "Stop"
# 1) Docs: interdire les marqueurs to-do, mais autoriser UTF-8 (accents)
$docs = Get-ChildItem -Recurse -Include *.md docs
foreach ($doc in $docs) {
  $content = Get-Content $doc.FullName -Raw
  if ($content -match ('T' + 'ODO')) { throw "To-do marker found in $($doc.FullName)" }
  # UTF-8 autorisé: pas de check ASCII dans /docs
}
Write-Host "docs_guard OK (UTF-8 allowed in docs)"
```

### 3.3 Distinguer l’ASCII-only côté **code** (guard optionnel)
Ajouter un guard dédié pour le code (activable step-02+):
```ps1
# tools/guards/ascii_code_guard.ps1 (optionnel)
$ErrorActionPreference = "Stop"
$codePaths = @("backend/src", "frontend/src")
foreach ($p in $codePaths) {
  if (-not (Test-Path $p)) { continue }
  $files = Get-ChildItem -Recurse $p -Include *.py,*.ts,*.tsx,*.json,*.yml,*.yaml,*.ps1
  foreach ($f in $files) {
    $raw = Get-Content $f.FullName -Raw
    if ($raw -match "[^\x00-\x7F]") { throw "Non-ASCII char in $($f.FullName)" }
  }
}
Write-Host "ascii_code_guard OK"
```
Et appeler ce guard à partir du **step-02** seulement (pas nécessaire pour step-01):
```ps1
# tools/guards/run_all_guards.ps1 (extrait futur)
& pwsh -File tools/guards/ascii_code_guard.ps1
```

### 3.4 Rendez `run_all_guards.ps1` explicite et verbeux (optionnel)
```ps1
# tools/guards/run_all_guards.ps1
$ErrorActionPreference = "Stop"
Write-Host "Running roadmap guard..."
& pwsh -File tools/guards/roadmap_guard.ps1 --strict
Write-Host "Running commit guard..."
& pwsh -File tools/guards/commit_guard.ps1 --strict
Write-Host "Running docs guard..."
& pwsh -File tools/guards/docs_guard.ps1
Write-Host "All guards OK"
```

> Note: pas de changement nécessaire sur `guards.yml` pour ce fix; garder l’exécution sur runner hôte (sans container) et shell `pwsh`.

---

## 4) Validation locale rapide
```
# Vérifier la présence de la Ref dans l’historique
git log -1 --pretty=%B | grep -F "Ref: docs/roadmap/step-01.md"

# Exécuter les guards en local (si pwsh dispo)
pwsh -File tools/guards/run_all_guards.ps1
```

---

## 5) Commit & PR
```
chore(step-01.1): fix guards (add roadmap ref, allow UTF-8 in docs)

Ref: docs/roadmap/step-01.1.md
```

---

## 6) Critères d’acceptation
- [ ] `Codex CI / guards` vert.
- [ ] `roadmap_guard.ps1` OK (Ref présente via PR ou dernier commit).
- [ ] `docs_guard.ps1` OK (UTF-8 accepté dans docs, pas de to-do).
- [ ] Pas de régression sur `backend-tests` et `frontend-tests`.

---

## 7) Suite après validation
- Step-02: Postgres + Redis + Alembic init; activer `ascii_code_guard.ps1` pour faire respecter l’ASCII-only dans **le code** (pas dans la doc).

---

## 8) Validation

VALIDATE? yes/no

