#!/bin/bash
# Setup script for ai-dev-workstation
# Creates a Python virtual environment, installs dependencies, and
# prepares a local .env file. Safe to re-run.

set -e

echo "======================================"
echo "ai-dev-workstation setup"
echo "======================================"

if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 not found. Please install Python 3 first."
    exit 1
fi

echo "Setting up Python virtual environment (.venv)..."
python3 -m venv .venv
# shellcheck disable=SC1091
source .venv/bin/activate

echo "Upgrading pip and installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo "Checking for Node.js/npm (only needed if you use npx-based MCP servers)..."
if command -v npm &> /dev/null; then
    echo "Node.js/npm found - npx-based MCP servers will work."
else
    echo "NOTE: Node.js/npm not found. Install it only if an MCP server in"
    echo ".vscode/mcp.json requires 'npx' (most of the defaults do)."
fi

echo "Making scripts executable..."
chmod +x scripts/*.sh scripts/*.py 2>/dev/null || true

if [ ! -f ".env" ]; then
    echo "Creating .env file from template..."
    cp .env.example .env
    echo "Edit .env and add only the API keys for the MCP servers you use."
else
    echo ".env file already exists - leaving it as is."
fi

echo ""
echo "Setup complete."
echo ""
echo "Next steps:"
echo "1. Edit .env with the keys you need (see .env.example for what each is for)."
echo "2. Run 'python3 scripts/validate-mcp-config.py' to check .vscode/mcp.json."
echo "3. Open this folder in VS Code via Remote-WSL and sign in to your coding agent."
echo ""
echo "See README.md for details."
