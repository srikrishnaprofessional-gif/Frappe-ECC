#!/usr/bin/env bash
# Install Frappe ECC into Claude Code (default) or Cursor.
#   ./install.sh                 Claude Code plugin, user scope
#   ./install.sh cursor [DIR]    Cursor rules into DIR/.cursor/rules
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
target="${1:-claude}"
case "$target" in
	claude) exec "$ROOT/bin/frappe-ecc" install claude "${@:2}" ;;
	cursor) exec "$ROOT/bin/frappe-ecc" install cursor --project "${2:-.}" ;;
	*) echo "usage: ./install.sh [claude|cursor [project-dir]]" >&2; exit 2 ;;
esac
