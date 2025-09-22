param()

$ErrorActionPreference = "Stop"

Write-Host "Seeding admin user (email: admin@example.com)..."
python backend/src/app/scripts/seed.py
