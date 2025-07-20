#!/bin/bash
# Setup script for AI Agent Development Workstation
# This script handles initial configuration and dependency installation

set -e

echo "======================================"
echo "AI Agent Development Workstation Setup"
echo "======================================"

# Create necessary directories
mkdir -p reports logs config scripts .vscode .venv

echo "Creating directory structure..."

# Set up Python virtual environment
if command -v python3 &> /dev/null; then
    echo "Setting up Python virtual environment..."
    python3 -m venv .venv
    source .venv/bin/activate
    echo "Virtual environment activated."
else
    echo "ERROR: Python 3 not found. Please install Python 3 first."
    exit 1
fi

echo "Upgrading pip and installing Python dependencies..."
if command -v pip &> /dev/null; then
    pip install --upgrade pip
    pip install -r requirements.txt
    echo "Python dependencies installed successfully"
else
    echo "ERROR: pip not found. Please ensure Python 3 and pip are installed."
    deactivate || true
    exit 1
fi

echo "Checking for Node.js/npm..."
if command -v npm &> /dev/null; then
    echo "Node.js/npm found - MCP servers will be available"
else
    echo "WARNING: Node.js/npm not found. MCP servers will not be available."
    echo "Install Node.js to enable MCP server functionality."
fi

echo "Making scripts executable..."
chmod +x scripts/*.sh scripts/*.py

if [ ! -f ".env" ]; then
    echo "Creating .env file from template..."
    cp .env.example .env
    echo "Please edit .env file and add your API keys and configuration"
else
    echo ".env file already exists"
fi

echo ""
echo "Setup completed successfully!"
echo "=========================="
echo ""
echo "Next steps:"
echo "1. Edit .env file and add your API keys"
echo "2. Run './scripts/weekly-update.sh' to test the automation"
echo "3. Set up weekly cron job or Windows Task Scheduler"
echo "4. Configure VS Code Insiders with the MCP servers"
echo ""
echo "For more information, see README.md"