param(
  [string]$RefLine = 'Ref: docs/roadmap/step-02.md',
  [string]$RepoSlug = '',
  [string]$Branch = ''
)
$ErrorActionPreference = 'Stop'
function Commit-EnsureRefLine { param([string]$line)
  $msg = git log -1 --pretty=%B
  if ($msg -notmatch [regex]::Escape($line)) { git commit --allow-empty -m $line }
}
function Push-WithFallback { param([string]$branch)
  try { if ($branch){ git push -u origin $branch } else { git push }; return } catch {
    $url = git remote get-url origin
    if ($url -like 'git@github.com:*') { $slug = $url -replace '^git@github.com:','' -replace '\.git$',''; git remote set-url origin ("https://github.com/${slug}.git") }
    if ($branch){ git push -u origin $branch } else { git push }
  }
}
function Ensure-PRBodyRef { param([string]$line)
  try { gh --version *> $null } catch { return }
  $n = (gh pr view --json number -q .number 2>$null)
  if (-not $n) { return }
  $b = (gh pr view --json body -q .body)
  if ($b -notmatch [regex]::Escape($line)) {
    $new = ($b + "`n`n" + $line).Trim()
    $tmp = Join-Path $env:TEMP 'pr_body_with_ref.txt'
    $new | Out-File -Encoding UTF8 -FilePath $tmp
    gh pr edit $n --body-file $tmp
    Remove-Item $tmp -ErrorAction SilentlyContinue
  }
}
Commit-EnsureRefLine -line $RefLine
Push-WithFallback -branch $Branch
Ensure-PRBodyRef -line $RefLine
Write-Host 'ensure_roadmap_ref done.'
