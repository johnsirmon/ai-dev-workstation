#!/bin/bash
# Validate this reference setup without installing tools or writing credentials.

set -euo pipefail
cd -- "$(dirname -- "${BASH_SOURCE[0]}")"

if ! command -v python3 > /dev/null 2>&1; then
    echo "ERROR: Python 3 is not available. Install Python 3.10+ to run the validator." >&2
    exit 1
fi

python3 scripts/validate-mcp-config.py

printf '\nConfiguration checked. Nothing was installed.\n'
printf 'Open this folder in VS Code through the WSL extension and choose one coding agent.\n'
printf 'Optional MCP servers need Node.js and npm ci; see docs/mcp.md before enabling them.\n'
