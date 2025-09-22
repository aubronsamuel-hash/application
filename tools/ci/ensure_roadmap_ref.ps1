param(
    [string]$RefLine = 'Ref: docs/roadmap/step-02.md',
    [string]$RepoSlug = '',
    [string]$Branch = ''
)

$ErrorActionPreference = 'Stop'

function Ensure-OriginRemote {
    param([string]$slug)

    if (-not $slug) {
        return $null
    }

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

    $message = ''
    try {
        $message = git log -1 --pretty=%B 2>$null
    } catch {
        $message = ''
    }

    if (-not $message) {
        Write-Host 'Repository has no commits yet. Creating initial empty commit with roadmap reference...'
        git commit --allow-empty -m $line
        return
    }

    if ($message -notmatch [regex]::Escape($line)) {
        Write-Host 'Adding empty commit with roadmap reference...'
        git commit --allow-empty -m $line
    } else {
        Write-Host 'Last commit already contains roadmap reference.'
    }
}

function Push-WithFallback {
    param([string]$branch)

    if ($branch) {
        git push -u origin $branch
    } else {
        git push
    }

    if ($LASTEXITCODE -eq 0) {
        return
    }

    Write-Warning 'SSH push failed. Switching origin to HTTPS...'
    $url = git remote get-url origin 2>$null
    if ($url -like 'git@github.com:*') {
        $slug = $url -replace '^git@github.com:', '' -replace '\.git$', ''
        git remote set-url origin ("https://github.com/{0}.git" -f $slug)
    }

    if ($branch) {
        git push -u origin $branch
    } else {
        git push
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

    $prNumber = gh pr view --json number -q .number 2>$null
    if (-not $prNumber) {
        Write-Warning 'No PR detected; skipping PR body update.'
        return
    }

    $body = gh pr view --json body -q .body
    if ($body -notmatch [regex]::Escape($line)) {
        $newBody = ($body + "`n`n" + $line).Trim()
        $tempFile = Join-Path $env:TEMP 'pr_body_with_ref.txt'
        $newBody | Out-File -Encoding UTF8 -FilePath $tempFile
        gh pr edit $prNumber --body-file $tempFile
        Remove-Item $tempFile -ErrorAction SilentlyContinue
        Write-Host 'PR body updated with roadmap reference.'
    } else {
        Write-Host 'PR body already contains roadmap reference.'
    }
}

if ($RepoSlug) {
    Ensure-OriginRemote -slug $RepoSlug | Out-Null
}

Commit-EnsureRefLine -line $RefLine
Push-WithFallback -branch $Branch
Ensure-PRBodyRef -line $RefLine

Write-Host 'Done.'
