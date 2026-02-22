# Copilot Instructions for AI Agent Developer Workstation

## Project Overview

This repository is a modular, self-updating AI Agent developer environment. It automates tool discovery, trend monitoring, and documentation updates using scripts and MCP servers. The architecture is designed for extensibility, automation, and integration with external AI/ML tools and platforms.

## Key Components & Structure

- **scripts/**: Automation scripts for monitoring, updating, and utility functions.  
  - update-tools.py: Checks tool versions and updates README with new findings.
  - forum-monitor.py: Scans GitHub, Reddit, and Hacker News for trending AI topics.
  - utils.py: Shared helpers for scripts.
- **config/**: Configuration files for tool tracking and MCP server setup.
- **README.md**: Main documentation, auto-updated with tool trends and setup instructions.
- **setup.sh**: Shell script for initial environment setup.
- **requirements.txt**: Python dependencies for scripts.
- **.github/workflows/auto-update.yml**: GitHub Actions workflow for weekly automation.

## Architecture & Data Flow

- **Trend Monitoring**:  
  - forum-monitor.py fetches data from GitHub, Hacker News, and other sources.
  - Results are analyzed and categorized by priority.
  - update-tools.py checks version updates and merges new trends into README.md.
- **Self-Updating Documentation**:  
  - GitHub Actions (auto-update.yml) runs scripts weekly, commits changes if updates are found.
- **MCP Server Integration**:  
  - Configuration in config/tools-tracking.json and .vscode/mcp.json.
  - Enables file system, web search, and GitHub access for automation.

## Developer Workflows

- **Setup**:  
  - Run setup.sh to install Python, Node, and MCP dependencies.
  - Use Makefile targets (setup, install, update, start, stop, clean) for common tasks.
- **Automation**:  
  - Weekly updates are triggered by GitHub Actions.
  - Manual update: `bash scripts/weekly-update.sh` or `python3 scripts/update-tools.py`.
- **Configuration**:  
  - MCP servers require API keys in environment variables or config files.
  - Update .vscode/mcp.json to add/modify MCP servers (use `inputs` for secrets).

## Project-Specific Patterns

- **Script Entry Points**:  
  - All automation scripts are in scripts/ and use if __name__ == "__main__": for execution.
- **Trend Analysis**:  
  - Trending tools are categorized by priority and use case before updating documentation.
- **Documentation Updates**:  
  - Only the "Current Trending Tools to Investigate" section in README.md is auto-updated.
- **Config Management**:  
  - Use JSON for MCP server configuration; environment variables for secrets.

## Integration Points

- **External APIs**:  
  - GitHub, Brave Search, and MCP servers.
- **Docker**:  
  - docker-compose.yml for service orchestration (if present).
- **Python & Node**:  
  - Scripts may invoke both Python and Node tools.

## Examples

- **Add a new MCP server**:  
  Update .vscode/mcp.json, add an `inputs` entry for any required secrets, and reload VS Code.
- **Run trend monitoring manually**:  
  python3 scripts/forum-monitor.py
- **Update documentation**:  
  python3 scripts/update-tools.py

## Key Files & Directories

- scripts/update-tools.py – Tool version checking and README update logic
- scripts/forum-monitor.py – External community and trend discovery logic
- .vscode/mcp.json – MCP server configuration (use `inputs` for secrets)
- README.md – Main documentation, auto-updated
- .github/workflows/auto-update.yml – Automation workflow
