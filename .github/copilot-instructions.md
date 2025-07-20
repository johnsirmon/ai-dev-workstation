# Copilot Instructions for AI Agent Developer Workstation

## Project Overview

This repository is a modular, self-updating AI Agent developer environment. It automates tool discovery, trend monitoring, and documentation updates using scripts and MCP servers. The architecture is designed for extensibility, automation, and integration with external AI/ML tools and platforms.

## Key Components & Structure

- **scripts/**: Automation scripts for monitoring, updating, and utility functions.  
  - trend_monitor.py: Scans external sources for trending AI tools.
  - update_readme.py: Updates documentation with new findings.
  - utils.py: Shared helpers for scripts.
- **config/**: Configuration files for tool tracking and MCP server setup.
- **README.md**: Main documentation, auto-updated with tool trends and setup instructions.
- **setup.sh**: Shell script for initial environment setup.
- **requirements.txt**: Python dependencies for scripts.
- **.github/workflows/auto-update.yml**: GitHub Actions workflow for weekly automation.

## Architecture & Data Flow

- **Trend Monitoring**:  
  - trend_monitor.py fetches data from GitHub, Hacker News, and other sources.
  - Results are analyzed and categorized by priority.
  - update_readme.py merges new trends into README.md.
- **Self-Updating Documentation**:  
  - GitHub Actions (auto-update.yml) runs scripts weekly, commits changes if updates are found.
- **MCP Server Integration**:  
  - Configuration in config/tools-tracking.json and claude_desktop_config.json.
  - Enables file system, web search, and GitHub access for automation.

## Developer Workflows

- **Setup**:  
  - Run setup.sh to install Python, Node, and MCP dependencies.
  - Use Makefile targets (setup, install, update, start, stop, clean) for common tasks.
- **Automation**:  
  - Weekly updates are triggered by GitHub Actions.
  - Manual update: make update or python scripts/update_readme.py.
- **Configuration**:  
  - MCP servers require API keys in environment variables or config files.
  - Update config/claude_desktop_config.json to add/modify MCP servers.

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
  Update config/claude_desktop_config.json and restart Claude Desktop.
- **Run trend monitoring manually**:  
  python scripts/trend_monitor.py
- **Update documentation**:  
  python scripts/update_readme.py

## Key Files & Directories

- scripts/trend_monitor.py – External tool discovery logic
- scripts/update_readme.py – Documentation update logic
- config/claude_desktop_config.json – MCP server configuration
- README.md – Main documentation, auto-updated
- .github/workflows/auto-update.yml – Automation workflow
