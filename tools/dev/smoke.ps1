param(
    [string]$Url = "http://localhost:8000/api/v1/health"
)

$ErrorActionPreference = "Stop"

Write-Host "Running smoke check against $Url"
$response = Invoke-WebRequest -UseBasicParsing -Method Get -Uri $Url
if ($response.StatusCode -ne 200) {
    throw "Expected HTTP 200, got $($response.StatusCode)"
}

$body = $response.Content | ConvertFrom-Json
if ($body.status -ne 'ok') {
    throw "Unexpected payload: $($response.Content)"
}

Write-Host "Smoke check successful"
