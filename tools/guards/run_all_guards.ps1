$ErrorActionPreference = "Stop"

$guardsPath = $PSScriptRoot

Write-Host 'Running roadmap guard...'
& pwsh -File (Join-Path $guardsPath 'roadmap_guard.ps1') -Strict

Write-Host 'Running commit guard...'
& pwsh -File (Join-Path $guardsPath 'commit_guard.ps1') -Strict

Write-Host 'Running docs guard...'
& pwsh -File (Join-Path $guardsPath 'docs_guard.ps1')
