# Start GradeUp the CORRECT way (Compose — not Docker Desktop "Run" on a single image).
# Reuses heavy backend layers when possible; rebuilds only what changed.

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root

if (-not (Test-Path ".\backend\.env")) {
    Write-Host "Missing backend\.env — copy backend\.env.example to backend\.env and add your keys." -ForegroundColor Red
    exit 1
}

Write-Host "Stopping old Compose stack (if any)..." -ForegroundColor Cyan
docker compose down

Write-Host "Building/updating images (uses cache — much faster than --no-cache)..." -ForegroundColor Cyan
docker compose build

Write-Host "Starting backend + frontend on the same Docker network..." -ForegroundColor Cyan
Write-Host "First backend boot can take 15–30+ minutes while the embedding model downloads." -ForegroundColor Yellow
docker compose up -d

docker compose ps
Write-Host ""
Write-Host "Open: http://localhost:5173  (wait until backend is healthy / frontend starts)" -ForegroundColor Green
Write-Host "If something fails: docker compose logs backend --tail 50" -ForegroundColor Yellow
