#!/usr/bin/env bash
# ==============================================================================
# Frappe ECC — Universal Installation Script
# Usage: ./install.sh --profile [minimal|full] --target [antigravity|claude|cursor|all]
# ==============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if command -v python3 &> /dev/null; then
    python3 "${SCRIPT_DIR}/bin/frappe_ecc_install.py" "$@"
elif command -v python &> /dev/null; then
    python "${SCRIPT_DIR}/bin/frappe_ecc_install.py" "$@"
elif command -v node &> /dev/null; then
    node "${SCRIPT_DIR}/bin/frappe-ecc.js" "$@"
else
    echo "Error: Python 3 or Node.js is required to run the Frappe ECC installer." >&2
    exit 1
fi
