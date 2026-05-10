# Start FastAPI with the port from config (.env: API_PORT). Fails fast if the port is already in use.
$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

$py = Join-Path $PSScriptRoot ".venv311\Scripts\python.exe"
if (-not (Test-Path $py)) {
    Write-Error "Virtual env not found at .venv311. Create it with: py -3.11 -m venv .venv311"
    exit 1
}

$port = & $py -c "from config import settings; print(settings.API_PORT)"
$port = [int]$port.Trim()

$listeners = @(Get-NetTCPConnection -LocalPort $port -State Listen -ErrorAction SilentlyContinue)
if ($listeners.Count -gt 0) {
    $pids = $listeners | Select-Object -ExpandProperty OwningProcess -Unique
    Write-Host "Port $port is already in use (PID(s): $($pids -join ', '))."
    Write-Host "Stop the other process, e.g.: Stop-Process -Id <pid> -Force"
    Write-Host "Or pick another port: set API_PORT in .env and update frontend API URL."
    exit 1
}

& $py -m uvicorn main:app --host 127.0.0.1 --port $port
