# docs/roadmap/step-01.2.md — Fix guards (validation block + commit Ref + purge TODO)

Ref: docs/roadmap/step-01.2.md

---

## 1) Contexte
CI "Codex CI / guards" toujours KO.

**Logs fournis**
```
Run ./tools/guards/run_all_guards.ps1
Running roadmap guard...
Exception: tools/guards/roadmap_guard.ps1:20
Missing validation question in docs/roadmap/roadmap_step_1.1.md
Running commit guard...
Exception: tools/guards/commit_guard.ps1:13
Latest commit is missing roadmap reference
Running docs guard...
Exception: tools/guards/docs_guard.ps1:12
TODO found in docs/agents/agent.docs.md
```

## 2) Analyse
1) **Nom de fichier roadmap 1.1**: le guard lit `docs/roadmap/roadmap_step_1.1.md` au lieu de `docs/roadmap/step-01.1.md`. Il faut **renommer** pour respecter le pattern.  
2) **Validation manquante**: le guard exige la question de validation **exacte** `VALIDATE? yes/no` dans le fichier de l'étape.  
3) **Commit Ref manquante**: dernier commit sans ligne `Ref:` correspondante.  
4) **TODO dans docs**: `docs/agents/agent.docs.md` contient "TODO" → le guard docs échoue.

---

## 3) Correctifs à appliquer

### 3.1 Normaliser le nom et ajouter le bloc de validation
Renommer le fichier mal nommé et injecter le bloc attendu.

```
# Renommage (bash)
git mv docs/roadmap/roadmap_step_1.1.md docs/roadmap/step-01.1.md || true

# Ajouter à la fin de docs/roadmap/step-01.1.md (si absent)
printf "\n---\n\n## 8) Validation\n\nVALIDATE? yes/no\n" >> docs/roadmap/step-01.1.md
```

> Vérifier aussi `docs/roadmap/step-01.md` (step principal) et y ajouter le bloc si manquant :
```
printf "\n---\n\n## Validation\n\nVALIDATE? yes/no\n" >> docs/roadmap/step-01.md
```

### 3.2 Corriger la Ref manquante dans l'historique
Créer un commit vide dédié avec la référence **step-01.1** (pour refléter le correctif) **ou** amender le dernier commit.

**Option A — Commit vide**
```
git commit --allow-empty -m "chore(step-01.1): add roadmap reference\n\nRef: docs/roadmap/step-01.1.md"
```

**Option B — Amend**
```
msg=$(git log -1 --pretty=%B)
echo "$msg\n\nRef: docs/roadmap/step-01.1.md" | git commit --amend -F -
```

**Push avec fallback HTTPS si SSH échoue**
```
if ! git push; then
  origin=$(git remote get-url origin)
  echo "SSH push failed from: $origin"
  git remote set-url origin https://github.com/<OWNER>/<REPO>.git
  git push
fi
```

### 3.3 Purger les TODO des documents
Le guard docs interdit "TODO" dans **tous** les `.md` sous `docs/`.

```
# Remplacer TODO par NOTE (ou supprimer la ligne) dans tous les .md
# (ne modifie pas le code, uniquement la doc)
find docs -type f -name "*.md" -print0 | xargs -0 sed -i 's/TODO/NOTE/g'
```

> Si certaines occurrences doivent rester des listes d’action, préfère un libellé neutre ("NOTE" ou "A FAIRE (tracké en issue)") mais évite le mot exact "TODO".

---

## 4) (Rappel) Assouplissement du guard docs (UTF-8 autorisé)
S'assurer que `tools/guards/docs_guard.ps1` **n'interdit pas** les caractères non-ASCII dans `/docs/**` (patch précédemment livré au step-01.1). Si nécessaire, appliquer :

```ps1
# tools/guards/docs_guard.ps1
$ErrorActionPreference = "Stop"
$docs = Get-ChildItem -Recurse -Include *.md docs
foreach ($doc in $docs) {
  $content = Get-Content $doc.FullName -Raw
  if ($content -match "TODO") { throw "TODO found in $($doc.FullName)" }
}
Write-Host "docs_guard OK (UTF-8 allowed in docs)"
```

---

## 5) Validation locale rapide
```
# Présence du bloc de validation
grep -F "VALIDATE? yes/no" docs/roadmap/step-01.1.md

# Présence de la Ref dans l'historique
git log -1 --pretty=%B | grep -F "Ref: docs/roadmap/step-01.1.md"

# Purge TODO
grep -R "TODO" docs && echo "(should be empty)"
```

---

## 6) Commit & PR
```
chore(step-01.2): fix guards (validation block, commit Ref, purge TODO in docs)

Ref: docs/roadmap/step-01.2.md
```

---

## 7) Critères d’acceptation
- [ ] `Codex CI / guards` vert.  
- [ ] `roadmap_guard.ps1` OK (bloc de validation présent + Ref dans l'historique).  
- [ ] `docs_guard.ps1` OK (aucun TODO dans /docs, UTF-8 autorisé).  
- [ ] Pas de régression sur `backend-tests` et `frontend-tests`.

---

## 8) Suite
- Après validation, lancer **step-02** (Postgres + Redis + Alembic init) et activer `ascii_code_guard.ps1` pour forcer l'ASCII-only dans le **code** uniquement.

