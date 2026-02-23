# ai-dev-workstation
Modern AI Agent Development Toolkit — Windows 11 · WSL 2 · VS Code Insiders · GitHub Copilot Agent Mode

> **Automation Notice:** This repository includes a weekly automation pipeline that can research ecosystem changes and update tracked tool data plus selected README sections.

> **Audience:** Developers using **VS Code Insiders** on Windows 11 with GitHub Copilot (agent mode), Claude Code, WSL 2, and Azure resources.

---

## 1 · VS Code Insiders as the Control Center  

| Step | What to do | Why |
|------|------------|-----|
|1|Install **VS Code Insiders** and enable **Auto‑update** (Settings → *Update: Mode* → `none` so it pulls the **daily** build automatically).|Daily insiders now ship improved chat‑mode diagnostics and tool‑hover support|
|2|Create a *Profile* called **“Agent‑Dev”** to isolate your extensions and settings from regular coding.|Keeps MCP servers and agent‑specific snippets from cluttering other workspaces.|
|3|Install **GitHub Copilot Nightly** and enable *Agent Mode* (`"github.copilot.chat.enable": true`).|Gives you model/tool routing in the chat sidebar.|

### MCP servers quick‑start

```jsonc
// .vscode/mcp.json
{
  "servers": {
    "context7": {
      "command": "npx",
      "args": ["-y", "@upstash/context7-mcp"],
      "type": "stdio",
      "env": {
        "UPSTASH_REDIS_REST_URL": "${UPSTASH_REDIS_REST_URL}",
        "UPSTASH_REDIS_REST_TOKEN": "${UPSTASH_REDIS_REST_TOKEN}"
      }
    },
    "memory": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-memory"],
      "type": "stdio"
    },
    "brave-search": {
      "command": "npx",
      "args": ["-y", "@brave/brave-search-mcp-server", "--transport", "stdio"],
      "type": "stdio",
      "env": {
        "BRAVE_API_KEY": "${BRAVE_API_KEY}"
      }
    },
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "type": "stdio",
      "env": {
        "GITHUB_PERSONAL_ACCESS_TOKEN": "${GITHUB_TOKEN}"
      }
    },
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "--allowed-directory", "${workspaceFolder}"],
      "type": "stdio"
    }
  }
}
```

**When to spin up your own server**

| Create new MCP server when… | Re‑use an existing server when… |
|-----------------------------|---------------------------------|
|You need a custom tool (e.g., call an internal REST API, run a Kusto query).|You just need vector search, retrieval, or memory that a generic server already exposes.|
|Security requires you to run on localhost and audit code.|You trust the community‑maintained implementation.|

GitHub’s docs outline editing `mcp.json` in the *Tools* panel.

> **Gotcha ⚠️**: Two servers listening on the **same port (3917)** will silently fail; always increment the port or kill the other process first.

---

## 2 · Choosing Your Coding Copilot  

| Tool | Strengths | Watch‑outs |
|------|-----------|-----------|
|**GitHub Copilot** (agent mode) | Deep VS Code integration, Azure SRE agent preview announced at Build 2025 | Chat context limited to ~16 k tokens unless MCP tooling expands it.|
|**Claude Code** extension | 200 k+ context, excels at refactors; can share MCP servers. | Must select the **Claude** sidebar; easy to think you’re still in Copilot.|
|**Cursor** | Whole‑file edit commands, great for “make this async”.|Adds a separate forked VS Code; ingesting large repos can cause battery drain. User reports of “bugs from AI patches”.|

---

## 3 · Leading Agent Frameworks (Last 6 Months)

| Framework / Lib | Latest ver. | Killer features |
|-----------------|------------|-----------------|
|**CrewAI**|1.9.3 (Updated 2026-02-23)|Declarative YAML mission files, vector‑based memory, Agents → Roles → Tasks hierarchy.|
|**Microsoft Autogen**|0.7.5 (Updated 2026-02-23)|Replay analytics, compliance hooks, VS Code debug adapter.|
|**LangGraph**|1.0.9 (Updated 2026-02-23)|Graph‑style branching flows; easy to plug into LangChain tools.|
|**Semantic Kernel**|1.39.4 (Updated 2026-02-23)|Process Framework (durable orchestration) + C#/**Python** parity.|
|**GPTScript Agents**|Bleeding‑edge|Script agents in 10 lines; great for Kubernetes ops.|
|**Clio (CLI Copilot)**|Active|Executes shell commands safely with confirm step.|

See the ODSC roundup for nine more frameworks.

---

## 4 · Azure‑centric Agent Tooling  

* **Azure AI Foundry**—“agent factory” announced at Build 2025. Adds governed deployment, Deep Research API (public preview)  
* **Project Amelie**—auto‑builds ML pipelines from one prompt  

Integrate via the new `azure-ai-foundry` Python SDK:

```bash
pip install azure-ai-foundry
foundry run --config foundry.yaml
```

---

## 5 · Environment Strategy: WSL 2 vs Windows vs Docker  

| Scenario | Best choice | Rationale |
|----------|-------------|-----------|
|Python‑heavy agent dev, need Linux tooling | **WSL 2** (Ubuntu 24.04) | Fast NT‑FS <-> ext4 I/O, GPU‑CUDA via DXGI.|
|Stable, reproducible runtime for others | **Docker Desktop** | Image pinning; runs same in CI.|
|GPU workloads w/ DirectML | **Windows native** | Avoid virtualization overhead.|

### Keep WSL fresh  

```powershell
wsl --update
wsl --shutdown
wsl --install Ubuntu-24.04
sudo apt update && sudo apt full-upgrade
```

(Install custom ISOs if 24.04 hasn’t hit the Store yet.)

---

## 6 · Performance & Daily Ops Tips  

- **Pin heavy extensions** (Python, Docker) to Windows profile; keep WSL profile lean.  
- Use `code-insiders .` **inside** WSL for lower latency on large repos.  
- Limit Docker Desktop to **4 GB RAM** unless building large images to save host resources.

---

## 7 · Where to Watch the Frontier  

| Community | Why follow |
|-----------|-----------|
|**OpenAI Developer Forum** | Early docs on Assistants API & function calling updates.|
|**LangChain Slack / Discord** | Rapid Q&A on LangGraph templates.|
|**Autogen GitHub Discussions** | Microsoft engineers share design patterns weekly.|
|**Azure AI Foundry Blog** | Enterprise agent governance & roadmap.|

---

## 8 · 30‑Second Setup Checklist  

- [ ] VS Code Insiders + Copilot Nightly installed  
- [ ] `.vscode/mcp.json` with at least one local server  
- [ ] WSL 2 Ubuntu 24.04 fully upgraded  
- [ ] Docker Desktop with WSL integration ON  
- [ ] `crewAI`, `autogen`, `semantic-kernel` installed in chosen environment  
- [ ] Azure credentials in `az login` & `foundry auth`  

> **Done!** You’re ready to build and ship multi‑agent apps on your Windows workstation without surprises.

---

## Self-Updating Documentation System

This workstation includes automated weekly research and update jobs to keep your AI agent development environment current:

### Automated Update Features

| Component | What it does | Frequency |
|-----------|-------------|-----------|
|**Tool Version Tracking**|Checks PyPI, npm, and GitHub for updates to all tracked frameworks|Weekly|
|**Community Monitoring**|Scans GitHub conversations, Reddit, and Hacker News for trending topics|Weekly|
|**Trending Tool Discovery**|Identifies new AI agent tools and frameworks gaining popularity|Weekly|
|**Signal Ranking + Dedup**|Ranks topics by relevance, freshness, and engagement and removes near-duplicates|Weekly|
|**README Auto-Updates**|Updates version numbers and trending tools section in this document|Weekly|

### MCP Server Configuration

Your `.vscode/mcp.json` is configured with:
- **Context7** for enhanced AI context management
- **Memory server** for persistent agent sessions
- **Brave Search** for real-time information access
- **GitHub integration** for repository management
- **Filesystem access** for local development

### Running Updates

```bash
# Manual update (weekly automation recommended)
./scripts/weekly-update.sh

# Check individual components
python3 scripts/update-tools.py
python3 scripts/forum-monitor.py
python3 scripts/validate-mcp-config.py
```

### Setup Automation

```bash
# GitHub Actions automation (already configured)
# .github/workflows/auto-update.yml runs every Monday at 09:00 UTC

# Set up weekly cron job (Linux/WSL)
echo "0 9 * * 1 cd /path/to/ai-dev-workstation && ./scripts/weekly-update.sh" | crontab -

# Or use Windows Task Scheduler for weekly runs
```

### Environment Variables for MCP Servers

Create a `.env` file in your project root:

```bash
# Upstash Redis (for Context7)
UPSTASH_REDIS_REST_URL=your_redis_url
UPSTASH_REDIS_REST_TOKEN=your_redis_token

# Brave Search API (for Brave Search MCP)
BRAVE_API_KEY=your_brave_search_api_key

# GitHub integration
GITHUB_TOKEN=your_github_personal_access_token
```

---

*Generated August 13, 2025 - updated by weekly automation or manual runs.*  


---

## Trending Tools to Investigate

| Tool | Stars | Language | Use Case | Repository |
|------|-------|----------|----------|------------|
|**parallel-code**|199|TypeScript|Run Claude Code, Codex, and Gemini side by side — each in      its own git worktree|[GitHub](https://github.com/johannesjo/parallel-code)|
|**conductor-orchestrator-superpowers**|193|Python|Multi-agent orchestration system for Claude Code with parallel execution, automated quality gates, B...|[GitHub](https://github.com/Ibrahim-3d/conductor-orchestrator-superpowers)|
|**BMAD_Openclaw**|130|N/A|Bridging the BMad Method to OpenClaw: 12-agent AI dev team using sessions_spawn|[GitHub](https://github.com/ErwanLorteau/BMAD_Openclaw)|
|**pantalk**|97|Go|Give your AI agent a voice on every chat platform.|[GitHub](https://github.com/pantalk/pantalk)|
|**librarium**|89|TypeScript|Multi-provider deep research CLI — fans out queries to multiple search/AI APIs in parallel|[GitHub](https://github.com/jkudish/librarium)|
|**CommonGround**|88|Python|The Sociotechnical OS for Multi-Agent Collaboration|[GitHub](https://github.com/Intelligent-Internet/CommonGround)|
|**openbrowserclaw**|87|TypeScript|Browser-native personal AI assistant. Zero infrastructure, the browser is the server.|[GitHub](https://github.com/sachaa/openbrowserclaw)|
|**aqua**|82|Go|Aqua, a cli message tool for AI agents |[GitHub](https://github.com/quailyquaily/aqua)|
|**OpenClaw-Book**|75|N/A|《深入 OpenClaw》。全网第一本介绍 OpenClaw 的书，用 OpenClaw + OpenCode + Opus 4.6 写成。A book introducing OpenClaw, w...|[GitHub](https://github.com/0xtresser/OpenClaw-Book)|
|**clawapp**|67|JavaScript|📱 ClawApp — Mobile H5 chat client for OpenClaw AI Agent platform. 用手机和你的 AI 智能体聊天。|[GitHub](https://github.com/qingchencloud/clawapp)|
