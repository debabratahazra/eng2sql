#!/usr/bin/env bash
# run_app.sh — Start the Eng2SQL Streamlit app inside WSL2 and open it in the
# default Windows browser.
#
# Usage (from WSL2 terminal, repo root or scripts/ directory):
#   bash scripts/run_app.sh            # default port 8501
#   bash scripts/run_app.sh 8502       # custom port
#
# Requirements:
#   - Python 3.11+ available as `python3` or `python`
#   - A virtual environment at <repo-root>/.venv  OR  packages installed globally
#   - A .env file at <repo-root>/.env  (copy from .env.example and fill in values)

set -euo pipefail

# ── Resolve repo root (works whether called from scripts/ or repo root) ───────
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

PORT="${1:-8501}"
HOST="localhost"
APP_PATH="${REPO_ROOT}/src/app.py"
VENV_DIR="${REPO_ROOT}/.venv"
ENV_FILE="${REPO_ROOT}/.env"

# ── Colour helpers ────────────────────────────────────────────────────────────
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'  # no colour

info()    { echo -e "${GREEN}[eng2sql]${NC} $*"; }
warn()    { echo -e "${YELLOW}[eng2sql]${NC} $*"; }
error()   { echo -e "${RED}[eng2sql]${NC} $*" >&2; }

# ── Preflight checks ─────────────────────────────────────────────────────────
if [[ ! -f "${APP_PATH}" ]]; then
    error "src/app.py not found — run this script from the repository root or scripts/ directory."
    exit 1
fi

if [[ ! -f "${ENV_FILE}" ]]; then
    warn ".env not found at ${ENV_FILE}. Copy .env.example and fill in your credentials:"
    warn "  cp ${REPO_ROOT}/.env.example ${REPO_ROOT}/.env"
    warn "Continuing without .env — environment variables must be set externally."
fi

# ── Activate virtual environment (if present) ────────────────────────────────
if [[ -d "${VENV_DIR}" ]]; then
    # shellcheck disable=SC1091
    source "${VENV_DIR}/bin/activate"
    info "Activated virtual environment: ${VENV_DIR}"
else
    warn ".venv not found — using system Python. To create one:"
    warn "  python3 -m venv ${VENV_DIR} && source ${VENV_DIR}/bin/activate && pip install -r ${REPO_ROOT}/requirements.txt"
fi

# ── Resolve Python / Streamlit ───────────────────────────────────────────────
PYTHON_BIN="$(command -v python3 2>/dev/null || command -v python 2>/dev/null || true)"
if [[ -z "${PYTHON_BIN}" ]]; then
    error "Python 3 not found. Install Python 3.11+ and try again."
    exit 1
fi

STREAMLIT_BIN="$(command -v streamlit 2>/dev/null || true)"
if [[ -z "${STREAMLIT_BIN}" ]]; then
    error "streamlit not found. Install dependencies with:"
    error "  pip install -r ${REPO_ROOT}/requirements.txt"
    exit 1
fi

info "Python  : ${PYTHON_BIN} ($(${PYTHON_BIN} --version 2>&1))"
info "Streamlit: ${STREAMLIT_BIN}"
info "Port    : ${PORT}"

# ── Open browser (WSL2 → Windows default browser via cmd.exe / powershell) ───
# WSL2 can reach Windows executables through the interop layer.
open_browser() {
    local url="http://${HOST}:${PORT}"
    # Small delay so Streamlit has time to bind the port before the browser tries
    sleep 3

    if command -v cmd.exe &>/dev/null; then
        # Fastest path: cmd.exe START opens the URL in the default Windows browser
        cmd.exe /c "start ${url}" 2>/dev/null &
    elif command -v powershell.exe &>/dev/null; then
        powershell.exe -NoProfile -Command "Start-Process '${url}'" 2>/dev/null &
    elif command -v wslview &>/dev/null; then
        # wslu package provides wslview for open-in-Windows-browser
        wslview "${url}" &
    elif command -v xdg-open &>/dev/null; then
        xdg-open "${url}" &
    else
        warn "Could not detect a browser launcher. Open manually: ${url}"
    fi
}

open_browser &

# ── Launch Streamlit ─────────────────────────────────────────────────────────
info "Starting Eng2SQL → http://${HOST}:${PORT}"
info "Press Ctrl+C to stop."
echo ""

cd "${REPO_ROOT}"
exec streamlit run "${APP_PATH}" \
    --server.port "${PORT}" \
    --server.address "${HOST}" \
    --server.headless true \
    --browser.gatherUsageStats false
