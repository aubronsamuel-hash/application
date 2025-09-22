$ErrorActionPreference = "Stop"

$docs = Get-ChildItem -Path (Join-Path $PSScriptRoot '..' '..' 'docs') -Recurse -Filter '*.md'
foreach ($doc in $docs) {
    $lines = Get-Content -Path $doc.FullName
    if ($lines -match 'TODO') {
        throw "TODO found in $($doc.FullName)"
    }

    foreach ($line in $lines) {
        if ($line.ToCharArray() | Where-Object { [int]$_ -gt 127 }) {
            throw "Non-ASCII character detected in $($doc.FullName)"
        }
    }
}

Write-Host 'docs_guard OK'
