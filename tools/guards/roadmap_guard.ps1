param([switch]$Strict)
$ErrorActionPreference = 'Stop'
$requiredRef = 'Ref: docs/roadmap/step-02.md'

function Get-LastCommitMessage { git log -1 --pretty=%B }
function Get-PRBody {
  if ($env:PR_BODY) { return $env:PR_BODY }
  if ($env:GITHUB_EVENT_NAME -eq 'pull_request') {
    try { $b = gh pr view --json body -q .body 2>$null; if ($LASTEXITCODE -eq 0 -and $b) { return $b } } catch {}
  }
  return ''
}

$commitMessage = Get-LastCommitMessage
if (-not $commitMessage.Contains($requiredRef)) { throw ("Missing roadmap reference in LAST COMMIT. Expected line: \"{0}\"" -f $requiredRef) }

$prBody = Get-PRBody
if ($env:GITHUB_EVENT_NAME -eq 'pull_request' -and -not $prBody.Contains($requiredRef)) {
  throw ("Missing roadmap reference in PR BODY. Expected line: \"{0}\"" -f $requiredRef)
}
Write-Host 'roadmap_guard OK'
