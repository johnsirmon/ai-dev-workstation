# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is an AI development workstation setup repository focused on modern AI agent development using VS Code Insiders on Windows 11 with WSL 2. The project serves as a comprehensive guide for developers working with AI agents, MCP servers, and various AI frameworks.

## Key Architecture Components

### Development Environment Stack
- **VS Code Insiders** as the primary IDE with agent-specific profiles
- **WSL 2 Ubuntu 24.04** for Linux tooling and Python development
- **GitHub Copilot** (agent mode) and **Claude Code** as AI coding assistants
- **MCP (Model Context Protocol)** servers for enhanced AI capabilities
- **Azure AI Foundry** integration for enterprise agent deployment

### MCP Server Configuration
The repository references MCP server setup in `.vscode/mcp.json` with servers like:
- `context7` for enhanced context management
- `memory` for persistent memory across sessions

### Supported AI Frameworks
The documentation covers multiple agent frameworks:
- **CrewAI** (0.140.0) - Declarative YAML mission files
- **Microsoft Autogen** (0.2) - Replay analytics and compliance hooks
- **LangGraph** - Graph-style branching flows
- **Semantic Kernel** (1.35.0) - Process Framework with C#/Python parity
- **GPTScript Agents** - Script agents for Kubernetes operations

## Environment Setup Commands

### WSL 2 Management
```bash
# Update WSL
wsl --update
wsl --shutdown
wsl --install Ubuntu-24.04

# Keep WSL fresh
sudo apt update && sudo apt full-upgrade
```

### Azure AI Foundry Setup
```bash
# Install Azure AI Foundry SDK
pip install azure-ai-foundry

# Run foundry configurations
foundry run --config foundry.yaml

# Authenticate
az login
foundry auth
```

### VS Code Integration
```bash
# Launch VS Code Insiders from WSL for lower latency
code-insiders .
```

## Development Workflow

### Profile Management
- Use "Agent-Dev" profile in VS Code Insiders to isolate agent-specific extensions
- Pin heavy extensions (Python, Docker) to Windows profile
- Keep WSL profile lean for performance

### Docker Configuration
- Limit Docker Desktop to 4 GB RAM unless building large images
- Enable WSL integration in Docker Desktop settings

## Project Structure

This is primarily a documentation and configuration repository with:
- `README.md` - Comprehensive setup guide and framework comparisons
- Future MCP server configurations
- Development environment templates

## Common Tasks

Since this is a documentation repository, common tasks involve:
1. Updating framework version information
2. Adding new MCP server configurations
3. Expanding environment setup instructions
4. Adding new AI framework integrations

## Important Notes

- MCP servers on the same port (3917) will silently fail - always increment ports
- Use WSL 2 for Python-heavy agent development
- Keep framework versions current as the ecosystem evolves rapidly
- Follow the 30-second setup checklist for quick environment validation