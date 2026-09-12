<h1 align="center">AI Dev Workstation</h1>

<p align="center">
  <strong>Windows comfort. Linux tooling. AI-assisted development.</strong><br>
  A lightweight reference for Windows 11, WSL 2, and VS Code.
</p>

<p align="center">
  <a href="#architecture">Architecture</a> &nbsp;&middot;&nbsp;
  <a href="#quick-start">Quick start</a> &nbsp;&middot;&nbsp;
  <a href="#optional-tools">Optional tools</a> &nbsp;&middot;&nbsp;
  <a href="#safety-boundaries">Safety</a>
</p>

![Windows 11 hosts the VS Code UI. The WSL extension connects it to VS Code Server, repository tools, and coding agents in Ubuntu. Agents connect to model providers; optional MCP tools connect to external services. The workflow is plan, edit, test, human review, then merge.](docs/images/architecture.png)

<p align="center"><sub>Conceptual architecture &middot; <a href="docs/images/architecture.png">View full-size</a></sub></p>

**A guide, not a framework or an installer bundle.** Start with an editor, a Linux workspace,
and one coding agent. Add tools only when they solve a real problem.
The repository's validator uses Python's standard library: no pip packages, containers,
agent SDKs, or orchestration services are required.

## Architecture

| Layer | What belongs here | Why it matters |
|---|---|---|
| **Windows host** | Windows 11 and the VS Code UI | Keep your familiar desktop and editor. |
| **WSL 2 / Ubuntu** | VS Code Server, source files, Git, terminals, Linux toolchains, and workspace-local MCP processes | Run Linux-first development tools alongside your code. |
| **External services** | Model providers and any GitHub, documentation, or search services you enable | Make data leaving the workstation an explicit choice. |

The [WSL extension](https://code.visualstudio.com/docs/remote/wsl) connects the Windows UI to
the Linux workspace. Extension placement depends on the extension; not every agent or
extension runs in Linux. The illustration is conceptual, not a process map.

**Coding agents** plan, edit, and use tools. **MCP servers** provide additional tools and data;
they are not required to call a model. **Agent frameworks** coordinate custom workflows and
are optional, bring-your-own components. None are installed by this repository.

## Quick start

### 1. Prepare Windows

In **PowerShell as Administrator**, if WSL is not already installed:

```powershell
wsl --install -d Ubuntu-24.04
```

Restart if prompted, then open Ubuntu and finish creating your Linux user.
Install [VS Code for Windows](https://code.visualstudio.com/download) and its
[WSL extension](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-wsl).
For an existing installation, use `wsl --update` to update WSL.

### 2. Open a Linux workspace

In **Ubuntu**, ensure Git and Python 3.10+ are available
(`sudo apt update && sudo apt install git python3` if needed), then:

```bash
mkdir -p ~/src
cd ~/src
git clone https://github.com/johnsirmon/ai-dev-workstation.git
cd ai-dev-workstation
bash setup.sh
code .
```

[setup.sh](setup.sh) checks the configuration without installing packages, creating a virtual
environment, or writing credentials. Keep Linux projects in the
[WSL filesystem](https://learn.microsoft.com/windows/wsl/filesystems#file-storage-and-performance-across-file-systems)
for Linux-tool performance. Confirm VS Code shows a **WSL** connection before running tools.

### 3. Choose one agent

Install and sign in to your preferred coding agent. This guide uses
[GitHub Copilot](https://docs.github.com/en/copilot) in VS Code as its baseline.
Give it a small task, inspect the diff, and run the relevant checks.
**MCP is optional; skip it until you need it.**

## Optional tools

Choose tools by **repository context, tool permissions, review controls, data handling,
and cost**, not a model leaderboard. Terminal alternatives include
[Claude Code](https://code.claude.com/docs/en/overview),
[Codex](https://developers.openai.com/codex), and
[Gemini CLI](https://github.com/google-gemini/gemini-cli).
Check each project's current requirements and terms.

The starter [MCP configuration](.vscode/mcp.json) contains four optional local servers.
They require Node.js with `npx` in WSL; the basic guide and validator do not.

| Server | Adds | Credential |
|---|---|---|
| [Context7](https://github.com/upstash/context7) | Library documentation lookup | `CONTEXT7_API_KEY` |
| [Memory](https://github.com/modelcontextprotocol/servers/tree/main/src/memory) | A persistent local knowledge graph | None |
| [Filesystem](https://github.com/modelcontextprotocol/servers/tree/main/src/filesystem) | File tools, initially scoped to this workspace | None |
| [Brave Search](https://github.com/brave/brave-search-mcp-server) | Web search | `BRAVE_API_KEY` |

**[MCP setup and credentials](docs/mcp.md)** covers enabling only what you need, storage,
version updates, and an optional official GitHub connection. GitHub MCP is **not** included
in the starter. Neither these servers nor any agent frameworks are preinstalled.

## Safety boundaries

- **Keep credentials out of Git and prompts.** Ignoring a file prevents accidental tracking,
  not access by an agent. Never put secrets in the memory graph.
- **Review before granting access.** MCP servers execute third-party code with the launching
  user's permissions. Filesystem roots can change through the client; they are not a sandbox.
- **Treat retrieved content as untrusted.** Web pages, issues, and tool results can contain
  instructions that should not override your task or permissions.
- **Know what leaves the machine.** Agents may send code and context to model providers;
  remote tools may send queries or content to their services.
- **Keep a human at the merge boundary.** Inspect diffs and terminal commands; retain approval
  prompts. WSL is a development environment, **not a security sandbox**.

## The review loop

**Plan &rarr; Edit &rarr; Test &rarr; Human review &rarr; Merge**

Keep each change small, run the relevant checks, then follow the
[manual PR checklist](PR_CHECKLIST.md). For this repository, run these in Ubuntu:

```bash
python3 scripts/validate-mcp-config.py
python3 -m unittest discover -s tests -v
bash -n setup.sh
git diff --check
```

[CI](.github/workflows/validate.yml) checks syntax, JSON, configuration consistency, and
regression tests. Its token has `contents: read`; it does not commit, push, or merge.
There are no scheduled update jobs. Validation is not a security certification.

## Inside the repository

| Entry | Purpose |
|---|---|
| [README.md](README.md) | System design and minimal getting-started path |
| [docs/mcp.md](docs/mcp.md) | Optional MCP configuration and credential guidance |
| [docs/images/architecture.png](docs/images/architecture.png) | Architecture illustration |
| [.vscode/mcp.json](.vscode/mcp.json) / [config/tools-tracking.json](config/tools-tracking.json) | Server definitions and npm-package metadata |
| [scripts/](scripts/) / [tests/](tests/) | Small validation/review helpers and standard-library tests |
| [CLAUDE.md](CLAUDE.md) | Shared repository instructions for coding agents |

[Copilot's instructions](.github/copilot-instructions.md) point to [CLAUDE.md](CLAUDE.md)
instead of duplicating context. Adapt the guide to your projects; keep the toolchain small
and the decisions reviewable.
