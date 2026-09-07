# CLAUDE.md

This file provides guidance to AI coding agents (Claude Code and others) working in this
repository. It is the single source of truth for agent-facing repo context — if you add
instructions for another agent, point it here instead of duplicating content.

## Project overview

This repo is a personal reference setup for developing with AI coding agents on **Windows 11 +
WSL2 + VS Code**. It is documentation and small validation scripts, not a framework or product.
See `README.md` for the full guide.

## Key facts

- Target environment: WSL2 Ubuntu, VS Code with the Remote-WSL extension.
- Primary coding agent: GitHub Copilot (agent mode), used from inside VS Code.
- MCP servers are defined in `.vscode/mcp.json`; secrets are referenced as `${VAR_NAME}` and must
  come from the environment/`.env`, never hard-coded in the file.
- `config/tools-tracking.json` only tracks metadata for the MCP npm packages referenced in
  `.vscode/mcp.json` — it is not a general AI-tool/framework catalog.
- There is no scheduled automation that edits files or pushes commits. The only workflow
  (`.github/workflows/validate.yml`) is read-only validation (`contents: read`).

## Scripts

- `scripts/validate-mcp-config.py` — validates `.vscode/mcp.json` against
  `config/tools-tracking.json`, flags deprecated env vars, and (with `--check-registry`) checks
  that referenced npm packages exist. Stdlib-only, no network access required unless
  `--check-registry` is passed.
- `scripts/review-pr.ps1` — optional PowerShell helper that wraps `gh pr review/merge` for manual
  PR review (see `PR_CHECKLIST.md`). Requires the GitHub CLI (`gh`) to be authenticated.

## When making changes

- Keep the README's AI-tool section durable and neutral: prefer capability-based guidance (repo
  context, tool/terminal access, MCP support, review workflow, privacy, cost) over vendor hype or
  version numbers that go stale quickly.
- Don't reintroduce automation that commits or pushes to the repository without human review.
- Don't hard-code secrets in `.vscode/mcp.json`, `config/tools-tracking.json`, or any committed
  file — use `${VAR_NAME}` placeholders and document the variable in `.env.example`.
- If you update `.vscode/mcp.json`, run `python3 scripts/validate-mcp-config.py` and update
  `config/tools-tracking.json` and `README.md`'s MCP table to match.
