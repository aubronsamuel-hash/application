param(
    [switch]$Strict
)

$ErrorActionPreference = "Stop"

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
    if ($Strict -and $content -notmatch 'VALIDATE\?\s+(yes|no)') {
        throw "Missing validation question in $($file.FullName)"
    }

    if ($content -notmatch 'Ref: docs/roadmap/') {
        throw "Missing Ref line in $($file.FullName)"
    }
}

Write-Host 'roadmap_guard OK'
