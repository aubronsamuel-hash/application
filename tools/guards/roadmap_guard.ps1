param(
    [switch]$Strict
)

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

$roadmapPath = Join-Path $PSScriptRoot '..' '..' 'docs' 'roadmap'
if (-not (Test-Path $roadmapPath)) {
    throw "Roadmap folder not found at $roadmapPath"
}

$files = Get-ChildItem -Path $roadmapPath -Filter '*.md'
if ($files.Count -eq 0) {
    throw "No roadmap files found"
}

foreach ($file in $files) {
    $content = Get-Content -Path $file.FullName -Raw
    if ($Strict -and $content -notmatch 'VALIDATE\?\s+(yes/no|yes|no)') {
        throw "Missing validation question in $($file.FullName)"
    }

    if ($content -notmatch 'Ref: docs/roadmap/') {
        throw "Missing Ref line in $($file.FullName)"
    }
}

$commitMessage = Get-LastCommitMessage
if (-not $commitMessage) {
    throw 'Unable to read last commit message.'
}

if ($commitMessage -notmatch [regex]::Escape($requiredRef)) {
    throw ("Missing roadmap reference in LAST COMMIT. Expected line: `"{0}`"" -f $requiredRef)
}

$prBody = Get-PRBody
if ($env:GITHUB_EVENT_NAME -eq 'pull_request') {
    if (-not $prBody) {
        throw ("PR body not available to verify required roadmap reference: {0}" -f $requiredRef)
    } elseif ($prBody -notmatch [regex]::Escape($requiredRef)) {
        throw ("Missing roadmap reference in PR BODY. Expected line: `"{0}`"" -f $requiredRef)
    }
} elseif ($prBody) {
    if ($prBody -notmatch [regex]::Escape($requiredRef)) {
        throw ("Provided PR_BODY env value is missing required roadmap reference line: {0}" -f $requiredRef)
    }
}

Write-Host 'roadmap_guard OK.'
