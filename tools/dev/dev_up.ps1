param(
    [switch]$WithBuild
)

$ErrorActionPreference = "Stop"

$composeFile = Join-Path $PSScriptRoot '..' '..' 'docker' 'docker-compose.dev.yml'
if (-not (Test-Path $composeFile)) {
    throw "docker-compose file not found at $composeFile"
}

$arguments = @('compose', '-f', $composeFile, 'up', '-d')
if ($WithBuild) {
    $arguments += '--build'
}

Write-Host "Starting development stack using $composeFile"
& docker @arguments
