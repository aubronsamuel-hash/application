$ErrorActionPreference = "Stop"

$composeFile = Join-Path $PSScriptRoot '..' '..' 'docker' 'docker-compose.dev.yml'
if (-not (Test-Path $composeFile)) {
    throw "docker-compose file not found at $composeFile"
}

Write-Host "Stopping development stack using $composeFile"
& docker compose -f $composeFile down
