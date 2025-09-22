param(
    [switch]$Strict
)

$ErrorActionPreference = "Stop"

$commitMessage = git log -1 --pretty=%B
if (-not $commitMessage) {
    throw "Unable to read commit message"
}

if ($commitMessage -notmatch 'Ref: docs/roadmap/') {
    throw "Latest commit is missing roadmap reference"
}

if ($Strict -and $commitMessage -notmatch 'Ref: docs/roadmap/step-\d+') {
    throw "Latest commit reference is not pointing to a step"
}

Write-Host 'commit_guard OK'
