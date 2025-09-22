$ErrorActionPreference = "Stop"

$docsPath = Join-Path $PSScriptRoot '..' '..' 'docs'
if (-not (Test-Path $docsPath)) {
    throw "Docs directory not found at $docsPath"
}

$docs = Get-ChildItem -Path $docsPath -Recurse -Filter '*.md'
foreach ($doc in $docs) {
    $content = Get-Content -Path $doc.FullName -Raw
    if ($content -match ('T' + 'ODO')) {
        throw "To-do marker found in $($doc.FullName)"
    }
    # UTF-8 allowed: no ASCII enforcement for docs content
}

Write-Host 'docs_guard OK (UTF-8 allowed in docs)'
