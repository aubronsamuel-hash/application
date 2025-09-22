# Roadmap Step-02: Roadmap Reference Guard, PR Template, and CI/pwsh Fixes

> Status: DRAFT (ready to implement)
> Target branch: feat/roadmap-step-02
> Scope: CI guards, commit/PR conventions, documentation baseline

---

## 🎯 Goals

1) Enforce that every commit and PR referencing this step contains the roadmap reference line:

```
Ref: docs/roadmap/step-02.md
```

2) Fix CI guards to run reliably on Ubuntu 24.04 with `pwsh` without relying on a broken action reference.

3) Provide a PR template, a commit-message helper, and an optional auto-fix script that can inject the roadmap reference into the last commit and PR body.

4) Keep everything Windows-first for local dev (PowerShell 7 scripts) and compatible with GitHub Actions linux runner (`shell: pwsh`).

---

## ✅ Acceptance Criteria

- CI "guards" job passes on pull_request and push.
- The workflow does NOT use any invalid action like `uses: powershell/powershell@v1`.
- The guard script fails if the last commit AND the PR body both lack the roadmap reference.
- A PR template exists with a placeholder for the roadmap reference.
- A local helper script exists to add the roadmap reference to the last commit and to the PR body (best-effort, with HTTPS fallback if SSH push fails).
- Documentation is updated: how to fix the guard error locally in 1 command.

---

## 🔧 Changes (files to create/update)

### 1) `.github/PULL_REQUEST_TEMPLATE.md`

```md
## Summary

- Describe the change...

## Roadmap Reference

- Paste the roadmap step reference below (required):

Ref: docs/roadmap/step-02.md

## Testing

- How did you test this change?
```

Notes:
- Keep the exact `Ref: docs/roadmap/step-02.md` line in your PR when working on this step.

---

### 2) `.github/workflows/guards.yml`

Key points:
- Do NOT use `uses: powershell/powershell@v1` (there is no such action). You can run PowerShell directly with `shell: pwsh` on Ubuntu images.
- Keep `pwsh` steps minimal and use the repo scripts.

Example minimal job (adjust name and triggers to match the repo):

```yaml
name: guards

on:
  pull_request:
  push:

jobs:
  guards:
    runs-on: ubuntu-24.04
    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Setup Python (if needed by guards)
        uses: actions/setup-python@v5
        with:
          python-version: '3.12'

      - name: Run guards
        shell: pwsh
        run: ./tools/guards/run_all_guards.ps1
        env:
          PR_BODY: ${{ github.event.pull_request.body || '' }}
          GITHUB_EVENT_NAME: ${{ github.event_name }}
```

---

### 3) `tools/guards/run_all_guards.ps1`

Responsibilities:
- Call `roadmap_guard.ps1` and propagate failure.
- Future guards can be chained here.

Example content:

```powershell
param()

$ErrorActionPreference = 'Stop'

$guards = @(
    'roadmap_guard.ps1'
)

foreach ($g in $guards) {
    $name = Split-Path $g -Leaf
    Write-Host "Running $name..."
    & (Join-Path $PSScriptRoot $g)
    if ($LASTEXITCODE -ne 0) { throw ("{0} failed." -f $name) }
}

Write-Host 'All guards passed.'
```

---

### 4) `tools/guards/roadmap_guard.ps1`

Checks:
- If running on `pull_request`: verify the PR body contains the reference line.
- Always check the last commit message contains the reference line.
- Reference pattern is strict and case-sensitive by design.

```powershell
param()

$ErrorActionPreference = 'Stop'

$requiredRef = 'Ref: docs/roadmap/step-02.md'

function Get-LastCommitMessage {
    git log -1 --pretty=%B
}

function Get-PRBody {
    # Prefer environment injection from the workflow
    if ($env:PR_BODY) { return $env:PR_BODY }

    # Fallback: try gh CLI if available and event is pull_request
    if ($env:GITHUB_EVENT_NAME -eq 'pull_request') {
        try {
            $body = gh pr view --json body -q .body 2>$null
            if ($LASTEXITCODE -eq 0 -and $body) { return $body }
        } catch { }
    }

    return ''
}

$commitMessage = Get-LastCommitMessage
if (-not $commitMessage.Contains($requiredRef)) {
    Write-Error ("Missing roadmap reference in LAST COMMIT. Expected line: `"{0}`"" -f $requiredRef)
}

$prBody = Get-PRBody
if ($env:GITHUB_EVENT_NAME -eq 'pull_request') {
    if (-not $prBody.Contains($requiredRef)) {
        Write-Error ("Missing roadmap reference in PR BODY. Expected line: `"{0}`"" -f $requiredRef)
    }
}

Write-Host 'roadmap_guard OK.'
```

---

### 5) `tools/ci/ensure_roadmap_ref.ps1`

Purpose:
- Local helper to add the reference in the last commit and push.
- Also updates the PR body to include the reference (if `gh` is available).
- Handles `origin` remote setup and SSH->HTTPS fallback.

```powershell
param(
    [string]$RefLine = 'Ref: docs/roadmap/step-02.md',
    [string]$RepoSlug = '',                # e.g. aubronsamuel-hash/codex_app
    [string]$Branch = ''                   # e.g. feat/roadmap-step-02
)

$ErrorActionPreference = 'Stop'

function Ensure-OriginRemote {
    param([string]$slug)
    if (-not $slug) { return }

    $current = git remote get-url origin 2>$null
    if (-not $current) {
        Write-Host 'Configuring origin (SSH)...'
        git remote add origin ("git@github.com:{0}.git" -f $slug)
        $current = git remote get-url origin
    }
    return $current
}

function Commit-EnsureRefLine {
    param([string]$line)
    $msg = git log -1 --pretty=%B
    if ($msg -notmatch [regex]::Escape($line)) {
        Write-Host 'Adding empty commit with roadmap reference...'
        git commit --allow-empty -m $line
    } else {
        Write-Host 'Last commit already contains roadmap reference.'
    }
}

function Push-WithFallback {
    param([string]$branch)
    try {
        if ($branch) { git push -u origin $branch } else { git push }
        return
    } catch {
        Write-Warning 'SSH push failed. Switching origin to HTTPS...'
        $url = git remote get-url origin
        if ($url -like 'git@github.com:*') {
            $slug = $url -replace '^git@github.com:','' -replace '\.git$',''
            git remote set-url origin ("https://github.com/{0}.git" -f $slug)
        }
        if ($branch) { git push -u origin $branch } else { git push }
    }
}

function Ensure-PRBodyRef {
    param([string]$line)
    try {
        gh --version *> $null
    } catch {
        Write-Warning 'gh CLI not available; skipping PR body update.'
        return
    }

    $prnum = (gh pr view --json number -q .number 2>$null)
    if (-not $prnum) { Write-Warning 'No PR detected; skip body update.'; return }

    $body = (gh pr view --json body -q .body)
    if ($body -notmatch [regex]::Escape($line)) {
        $new = ($body + "`n`n" + $line).Trim()
        $tmp = Join-Path $env:TEMP 'pr_body_with_ref.txt'
        $new | Out-File -Encoding UTF8 -FilePath $tmp
        gh pr edit $prnum --body-file $tmp
        Remove-Item $tmp -ErrorAction SilentlyContinue
        Write-Host 'PR body updated with roadmap reference.'
    } else {
        Write-Host 'PR body already contains roadmap reference.'
    }
}

if ($RepoSlug) { Ensure-OriginRemote -slug $RepoSlug | Out-Null }
Commit-EnsureRefLine -line $RefLine
Push-WithFallback -branch $Branch
Ensure-PRBodyRef -line $RefLine

Write-Host 'Done.'
```

Usage:

```powershell
# Example (run locally):
./tools/ci/ensure_roadmap_ref.ps1 -RepoSlug "aubronsamuel-hash/codex_app" -Branch "feat/roadmap-step-02"
```

---

### 6) `docs/guards/README.md` (add quick troubleshooting)

```md
# Guards - Quick Troubleshooting

## Error: Missing 'Ref: docs/roadmap/step-02.md' in PR or last commit

**Fix locally:**

```powershell
./tools/ci/ensure_roadmap_ref.ps1 -RepoSlug "<owner>/<repo>" -Branch "<your-branch>"
```

This will:
- create an empty commit with the roadmap reference if missing,
- push (SSH, fallback to HTTPS if needed),
- update the PR body with the same reference when possible.

Also ensure your PR uses the template and keeps the `Ref:` line.
```

---

## 🧪 Local validation

```powershell
# 1) Run guards locally
./tools/guards/run_all_guards.ps1

# 2) Simulate PR body via env var (before pushing/opening PR)
$env:PR_BODY = (Get-Content -Raw ./.github/PULL_REQUEST_TEMPLATE.md)
$env:GITHUB_EVENT_NAME = 'pull_request'
./tools/guards/run_all_guards.ps1
```

---

## 🔁 Git flow for this step

- Create branch `feat/roadmap-step-02`.
- Commit your changes with a message that includes the reference line.
- Open PR; keep the `Ref: docs/roadmap/step-02.md` line in the PR body.
- Ensure CI is green.

Example commit message:

```
chore(ci): enforce roadmap reference in PR and last commit

Ref: docs/roadmap/step-02.md
```

---

## 📌 Notes

- On GitHub-hosted Ubuntu runners, `pwsh` is available. Prefer `shell: pwsh` in workflow steps and avoid non-existent marketplace actions.
- We inject `PR_BODY` via workflow env to make the guard deterministic even if `gh` is not available.

---

# PROMPT.codex.step-02 (Give this to Codex)

System:
You are CODEx, a repository automation engineer. You act on the current repo working directory. You write deterministic, ASCII-only changes. You create a new branch and open a PR if needed. You must keep commits small, atomic, and include the roadmap reference line.

User:
Implement Roadmap Step-02. Apply exactly the changes below. When done, run the guards locally if available, then push and open/update the PR.

Tasks:
1) Create/update these files exactly as specified by the roadmap:
   - .github/PULL_REQUEST_TEMPLATE.md (include the required `Ref: docs/roadmap/step-02.md` line section)
   - .github/workflows/guards.yml (run guards with `shell: pwsh`; NO `uses: powershell/powershell@v1`)
   - tools/guards/run_all_guards.ps1 (loop through guards; stop on error)
   - tools/guards/roadmap_guard.ps1 (check last commit AND PR body for the line `Ref: docs/roadmap/step-02.md`)
   - tools/ci/ensure_roadmap_ref.ps1 (helper to add empty commit with the reference, push with SSH->HTTPS fallback, and update PR body via gh)
   - docs/guards/README.md (add troubleshooting section)

2) Create branch `feat/roadmap-step-02` and commit changes using Conventional Commits. Ensure the last commit message body contains:

   Ref: docs/roadmap/step-02.md

3) Push the branch. If SSH push fails, automatically switch `origin` to HTTPS and re-push.

4) Open or update the PR. Ensure the PR body includes the same reference line. If `gh` is unavailable, rely on the PR template and/or the workflow-provided env var.

5) Re-run the CI guards and confirm they pass.

Output:
- A short checklist of files created/updated.
- The branch name and PR URL (if available).
- If anything fails, print the exact command(s) the human can run locally to fix it.

Constraints:
- ASCII only.
- Do not modify unrelated files.
- Keep changes idempotent.

END

