# ai-dev-workstation

A practical setup guide for developing with AI coding agents on **Windows 11 + WSL2 + VS Code**.

*Last reviewed: September 2026.*

This repo is a personal reference, not a framework — it documents one working setup and ships a
few small scripts to validate the configuration. AI vendor names, features, and pricing change
fast; treat anything below as a starting point and check the linked official docs before relying
on specifics.

## Quick start

**In PowerShell (Windows):**

```powershell
wsl --install -d Ubuntu-24.04   # first time only
wsl --update
winget install Microsoft.VisualStudioCode Git.Git
```

**In the WSL2 Ubuntu shell:**

```bash
sudo apt update && sudo apt full-upgrade -y
git clone https://github.com/johnsirmon/ai-dev-workstation.git
cd ai-dev-workstation
./setup.sh
```

Then in VS Code: install the **WSL** extension, run **"WSL: Connect to WSL"**, and open this
folder from inside the WSL window (`code .` from the WSL terminal also works). Install **GitHub
Copilot** (or your preferred coding agent extension) and sign in.

## Why WSL2 for this workflow

- Linux-native tooling (Python, Node, shell scripts) without path/line-ending friction.
- VS Code's Remote-WSL support means the editor UI stays on Windows while everything else runs in
  Linux — this is the officially recommended setup for Linux-first development on Windows.
- Docker Desktop, if you use it, should have WSL2 integration enabled for the same reason.

Keep WSL current (PowerShell):

```powershell
wsl --update
wsl --shutdown
```

## Choosing an AI coding agent

Don't try to run every agent at once. Pick **one primary agent** integrated into VS Code for daily
work, and add a CLI agent or extra MCP servers only when you have a specific need.

**What actually matters when choosing:**

- **Repository context** — can it see your whole workspace, not just the open file?
- **Terminal/tool access** — can it run tests, builds, and git commands, and do you trust the
  scope it's given?
- **MCP support** — can it use Model Context Protocol servers for extra tools/data sources?
- **Review workflow** — does it produce diffs/PRs you can review before merging, or edit silently?
- **Privacy & data controls** — what happens to your code/prompts (training use, retention,
  enterprise/business data-handling tiers)?
- **Cost and limits** — subscription vs. usage-based billing, and rate/context limits.

None of these are fixed facts about a vendor forever — check the current docs before deciding.

### Current tool landscape (verify before relying on details)

| Tool | What it is | Status / caveats |
|------|-----------|-------------------|
| [GitHub Copilot](https://docs.github.com/en/copilot) (Chat/Agent mode, coding agent) | Deep VS Code/GitHub integration; can run agentic, multi-file tasks and open PRs. | Primary recommendation for this repo's workflow since it's native to VS Code and GitHub. |
| [OpenAI Codex](https://developers.openai.com/codex) | OpenAI's agentic coding tool (CLI and IDE extension). | Model-agnostic within OpenAI's own models; check current CLI/extension docs for VS Code support. |
| [Claude Code](https://docs.claude.com/en/docs/claude-code/overview) | Anthropic's terminal-first coding agent, also available as an extension. | Strong for large-context refactors; runs outside the VS Code chat UI unless using the extension. |
| [Gemini CLI](https://github.com/google-gemini/gemini-cli) / [Gemini Code Assist](https://codeassist.google/) | Google's terminal agent and IDE assistant. | Gemini CLI is open source; Code Assist is the IDE-integrated product — check current free/paid tiers. |
| [Cursor](https://cursor.com) | AI-first fork of VS Code (by Anysphere). | Anysphere/Cursor became a SpaceX subsidiary in 2026. Functionality and roadmap may change under new ownership — check cursor.com for the current state before adopting it as a primary tool. |
| [Windsurf](https://windsurf.com) | AI-first IDE (originally Codeium). | Treat as optional/legacy context rather than a default pick; the competitive landscape around forked IDEs has shifted since 2025. Verify current status before recommending it to others. |

This list is intentionally short. For anything not listed (agent frameworks, orchestration SDKs,
model leaderboards, etc.), check the vendor's own documentation rather than a comparison blog —
that space moves too fast for a static table to stay accurate.

## MCP servers

[Model Context Protocol](https://modelcontextprotocol.io) (MCP) lets an agent call external tools
(search, GitHub, memory, filesystem, internal APIs) through a standard interface. This repo's
`.vscode/mcp.json` defines a small starter set:

| Server | Purpose | Secret required |
|--------|---------|------------------|
| `context7` | Up-to-date library docs/context lookup. | `CONTEXT7_API_KEY` |
| `memory` | In-session persistent notes/memory. | none |
| `filesystem` | Read/write access scoped to this workspace folder. | none |
| `github` | Repository/issue/PR access. | `GITHUB_TOKEN` (personal access token) |
| `brave-search` | Web search. | `BRAVE_API_KEY` |

Secrets are referenced as `${VAR_NAME}` in `mcp.json` and resolved from your environment or VS
Code's secret storage — **never hard-code a token in `mcp.json` or commit one to git.** Copy
`.env.example` to `.env`, fill in only the keys you actually need, and load it into your shell
(e.g. `export $(grep -v '^#' .env | xargs)` in bash) before starting VS Code from that shell.

**Least-privilege guidance:**
- Scope the GitHub token to the minimum permissions/repos you need, and prefer a fine-grained PAT.
- Only add MCP servers you understand — each one is code you're letting an agent invoke on your
  behalf. Remove servers you're not using from `mcp.json`.
- Don't grant an agent write access (git push, file deletion, package publishing) unless you
  review its proposed changes first. Prefer agents that show a diff/PR before applying edits.

Validate the config any time you edit it:

```bash
python3 scripts/validate-mcp-config.py
```

## Recommended baseline workflow

1. **VS Code + Remote-WSL** as the editor, running inside your Ubuntu WSL distro.
2. **One primary coding agent** wired into VS Code (GitHub Copilot by default in this repo).
3. **Git/GitHub** for review — let the agent propose changes as a diff or PR, don't let it push
   directly to a protected branch.
4. **MCP servers**, added incrementally, only for tools you actually need.
5. **Optional CLI agents** (Claude Code, Gemini CLI, Codex CLI) for tasks better suited to a
   terminal workflow (long-running scripts, headless environments) — keep credentials scoped the
   same way as above.

## Setup, update, and cleanup

| Task | Shell | Command |
|------|-------|---------|
| Install WSL2 + Ubuntu | PowerShell | `wsl --install -d Ubuntu-24.04` |
| Update WSL kernel | PowerShell | `wsl --update` |
| Update Ubuntu packages | Bash (WSL) | `sudo apt update && sudo apt full-upgrade -y` |
| Initial repo setup (venv, deps, `.env`) | Bash (WSL) | `./setup.sh` |
| Validate MCP config | Bash (WSL) | `python3 scripts/validate-mcp-config.py` |
| Validate Python syntax | Bash (WSL) | `python3 -m py_compile scripts/*.py` |
| Stop/reset WSL distro | PowerShell | `wsl --shutdown` |
| Remove local venv (clean) | Bash (WSL) | `rm -rf .venv` |

`setup.sh` creates a Python virtual environment, installs `requirements.txt` (currently empty —
kept for future scripts), makes the `scripts/` files executable, and copies `.env.example` to
`.env` if one doesn't already exist. It does not install Node.js; only install it if an MCP
server you use requires `npx`.

## Repository layout

```
.
├── .env.example              # Template for MCP server secrets — copy to .env, never commit .env
├── .vscode/mcp.json           # MCP server definitions used by VS Code
├── config/tools-tracking.json # Metadata cross-checked by scripts/validate-mcp-config.py
├── scripts/
│   ├── validate-mcp-config.py # Checks mcp.json against tracked servers, flags deprecated env vars
│   └── review-pr.ps1          # Optional helper: approve/merge a PR via `gh` CLI
├── setup.sh                   # One-time environment bootstrap
├── requirements.txt            # Python deps (currently none required)
├── CLAUDE.md                  # Agent-facing repo context (see below)
└── PR_CHECKLIST.md            # Manual PR review checklist
```

## Agent instructions

[`CLAUDE.md`](CLAUDE.md) is the single source of truth for repo context given to AI coding agents
(Claude Code and others that read it). If you add instructions for another agent, point it at
`CLAUDE.md` instead of duplicating content.

## Automation

There is no scheduled automation in this repo. Tool versions and AI product details age quickly
and are easy to get wrong when auto-generated, so this repo favors periodic manual review over a
background job that edits `README.md` or commits unreviewed content. If you want to re-introduce
scheduled checks, keep them read-only (validation only) or require a human to review the diff
before merge — never grant a scheduled workflow permission to push directly to your default
branch.
