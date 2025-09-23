param([switch]$Strict)
$ErrorActionPreference = 'Stop'
$requiredRef = 'Ref: docs/roadmap/step-02.md'

function Get-LastCommitMessage {
  git log -1 --pretty=%B
}

function Get-PRBody {
  if ($env:PR_BODY) {
    return $env:PR_BODY
  }

  if ($env:GITHUB_EVENT_NAME -eq 'pull_request') {
    try {
      $body = gh pr view --json body -q .body 2>$null
      if ($LASTEXITCODE -eq 0 -and $body) {
        return $body
      }
    } catch {
    }
  }

  return ''
}

$commitMessage = Get-LastCommitMessage
if ([string]::IsNullOrWhiteSpace($commitMessage) -or ($commitMessage -notlike "*${requiredRef}*")) {
  throw "Missing roadmap reference in LAST COMMIT. Expected line: '${requiredRef}'"
}

$prBody = Get-PRBody
if ($env:GITHUB_EVENT_NAME -eq 'pull_request' -and ($prBody -notlike "*${requiredRef}*")) {
  throw "Missing roadmap reference in PR BODY. Expected line: '${requiredRef}'"
}

Write-Host 'roadmap_guard OK'
