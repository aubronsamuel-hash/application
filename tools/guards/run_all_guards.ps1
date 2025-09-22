$ErrorActionPreference = 'Stop'

$guards = @(
    @{ Name = 'roadmap_guard.ps1'; Arguments = @('-Strict') },
    @{ Name = 'commit_guard.ps1'; Arguments = @('-Strict') },
    @{ Name = 'docs_guard.ps1'; Arguments = @() }
)

foreach ($guard in $guards) {
    $scriptPath = Join-Path $PSScriptRoot $guard.Name
    if (-not (Test-Path $scriptPath)) {
        throw ("Guard script not found: {0}" -f $guard.Name)
    }

    Write-Host ("Running {0}..." -f $guard.Name)

    $arguments = @()
    if ($guard.Arguments) {
        $arguments = $guard.Arguments
    }

    & $scriptPath @arguments

    if ($LASTEXITCODE -ne 0) {
        throw ("{0} failed with exit code {1}" -f $guard.Name, $LASTEXITCODE)
    }
}

Write-Host 'All guards passed.'
