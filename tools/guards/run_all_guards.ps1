$ErrorActionPreference = 'Stop'

& pwsh -File tools/guards/roadmap_guard.ps1 --strict
if ($LASTEXITCODE -ne 0) { throw 'roadmap_guard.ps1 failed.' }
& pwsh -File tools/guards/commit_guard.ps1 --strict
if ($LASTEXITCODE -ne 0) { throw 'commit_guard.ps1 failed.' }
& pwsh -File tools/guards/docs_guard.ps1
if ($LASTEXITCODE -ne 0) { throw 'docs_guard.ps1 failed.' }
Write-Host 'All guards OK'
