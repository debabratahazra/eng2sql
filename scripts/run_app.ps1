#Requires -Version 5.1
<#
.SYNOPSIS
    Start the Eng2SQL Streamlit app on Windows and open it in the default browser.

.DESCRIPTION
    Resolves the repo root, activates the .venv virtual environment if present,
    verifies Python and Streamlit are available, then launches the app.

.PARAMETER Port
    TCP port for Streamlit to listen on. Defaults to 8501.

.EXAMPLE
    .\scripts\run_app.ps1
    .\scripts\run_app.ps1 -Port 8502
    powershell -ExecutionPolicy Bypass -File scripts\run_app.ps1
#>
param(
    [int]$Port = 8501
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

# ── Resolve repo root ─────────────────────────────────────────────────────────
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
$RepoRoot  = (Resolve-Path (Join-Path $ScriptDir '..') ).Path

$Host_     = 'localhost'
$AppPath   = Join-Path $RepoRoot 'src\app.py'
$VenvDir   = Join-Path $RepoRoot '.venv'
$EnvFile   = Join-Path $RepoRoot '.env'

# ── Colour helpers ────────────────────────────────────────────────────────────
function Write-Info  { param([string]$Msg) Write-Host "[eng2sql] $Msg" -ForegroundColor Green  }
function Write-Warn  { param([string]$Msg) Write-Host "[eng2sql] $Msg" -ForegroundColor Yellow }
function Write-Err   { param([string]$Msg) Write-Host "[eng2sql] $Msg" -ForegroundColor Red    }

# ── Preflight checks ──────────────────────────────────────────────────────────
if (-not (Test-Path $AppPath)) {
    Write-Err "src\app.py not found — run this script from the repository root or scripts\ directory."
    exit 1
}

if (-not (Test-Path $EnvFile)) {
    Write-Warn ".env not found at $EnvFile. Copy .env.example and fill in your credentials:"
    Write-Warn "  Copy-Item $RepoRoot\.env.example $RepoRoot\.env"
    Write-Warn "Continuing without .env — environment variables must be set externally."
}

# ── Activate virtual environment (if present) ─────────────────────────────────
$VenvActivate = Join-Path $VenvDir 'Scripts\Activate.ps1'
if (Test-Path $VenvActivate) {
    & $VenvActivate
    Write-Info "Activated virtual environment: $VenvDir"
} else {
    Write-Warn ".venv not found — using system Python. To create one:"
    Write-Warn "  python -m venv $VenvDir"
    Write-Warn "  $VenvDir\Scripts\Activate.ps1"
    Write-Warn "  pip install -r $RepoRoot\requirements.txt"
}

# ── Resolve Python / Streamlit ────────────────────────────────────────────────
$PythonBin = (Get-Command python -ErrorAction SilentlyContinue)?.Source
if (-not $PythonBin) {
    Write-Err "Python not found. Install Python 3.11+ and ensure it is on your PATH."
    exit 1
}

$StreamlitBin = (Get-Command streamlit -ErrorAction SilentlyContinue)?.Source
if (-not $StreamlitBin) {
    Write-Err "streamlit not found. Install dependencies with:"
    Write-Err "  pip install -r $RepoRoot\requirements.txt"
    exit 1
}

$PythonVersion = & $PythonBin --version 2>&1
Write-Info "Python   : $PythonBin ($PythonVersion)"
Write-Info "Streamlit: $StreamlitBin"
Write-Info "Port     : $Port"

# ── Open browser after a short delay ─────────────────────────────────────────
$Url = "http://${Host_}:$Port"
$null = Start-Job -ScriptBlock {
    param($u)
    Start-Sleep -Seconds 3
    Start-Process $u
} -ArgumentList $Url

# ── Launch Streamlit ──────────────────────────────────────────────────────────
Write-Info "Starting Eng2SQL → $Url"
Write-Info "Press Ctrl+C to stop."
Write-Host ""

Set-Location $RepoRoot
& $StreamlitBin run $AppPath `
    --server.port $Port `
    --server.address $Host_ `
    --server.headless true `
    --browser.gatherUsageStats false
