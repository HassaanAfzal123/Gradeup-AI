# Tear down old GradeUp Docker state and rebuild from scratch (Windows PowerShell).
# Run from repo root:  .\scripts\docker-fresh.ps1

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root

if (-not (Test-Path ".\backend\.env")) {
    Write-Host "Create backend\.env first (copy from backend\.env.example and set GROQ_API_KEY, SECRET_KEY)." -ForegroundColor Yellow
    exit 1
}

Write-Host "Stopping and removing containers, networks, and named volumes for this compose project..." -ForegroundColor Cyan
docker compose down -v --remove-orphans

Write-Host "Building images (no cache)..." -ForegroundColor Cyan
docker compose build --no-cache

Write-Host "Starting stack..." -ForegroundColor Cyan
docker compose up -d

docker compose ps
Write-Host ""
Write-Host "UI:  http://localhost:5173/" -ForegroundColor Green
Write-Host "API: http://localhost:8000/" -ForegroundColor Green
Write-Host "First backend boot may take 2–3 minutes while embeddings load." -ForegroundColor Yellow
