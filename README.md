# ai-dev-workstation
basic setup for development on a Windows machine with WSL and vscode

> **Living Document Notice:** This document automatically updates itself nightly with the latest tool versions, community trends, and emerging frameworks. Changes are committed automatically in addition to manual updates.

# Modern AI Agent Development Toolkit — August 13, 2025

> **Audience:** Developers using **VS Code Insiders** on Windows 11 with GitHub Copilot (agent mode), Claude Code, WSL 2, and Azure resources.

---

## 1 · VS Code Insiders as the Control Center  

| Step | What to do | Why |
|------|------------|-----|
|1|Install **VS Code Insiders** and enable **Auto‑update** (Settings → *Update: Mode* → `none` so it pulls the **daily** build automatically).|Daily insiders now ship improved chat‑mode diagnostics and tool‑hover support citeturn0search4|
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
      "type": "stdio"
    },
    "memory": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-memory"]
    }
  }
}
```

**When to spin up your own server**

| Create new MCP server when… | Re‑use an existing server when… |
|-----------------------------|---------------------------------|
|You need a custom tool (e.g., call an internal REST API, run a Kusto query).|You just need vector search, retrieval, or memory that a generic server already exposes.|
|Security requires you to run on localhost and audit code.|You trust the community‑maintained implementation.|

GitHub’s docs outline editing `mcp.json` in the *Tools* panel citeturn0search0turn0search5.

> **Gotcha ⚠️**: Two servers listening on the **same port (3917)** will silently fail; always increment the port or kill the other process first.

---

## 2 · Choosing Your Coding Copilot  

| Tool | Strengths | Watch‑outs |
|------|-----------|-----------|
|**GitHub Copilot** (agent mode) | Deep VS Code integration, Azure SRE agent preview announced at Build 2025 citeturn1news32 | Chat context limited to ~16 k tokens unless MCP tooling expands it.|
|**Claude Code** extension | 200 k+ context, excels at refactors; can share MCP servers. | Must select the **Claude** sidebar; easy to think you’re still in Copilot.|
|**Cursor** | Whole‑file edit commands, great for “make this async”.|Adds a separate forked VS Code; ingesting large repos can cause battery drain. User reports of “bugs from AI patches” citeturn0news79.|

---

## 3 · Leading Agent Frameworks (Last 6 Months)

| Framework / Lib | Latest ver. | Killer features |
|-----------------|------------|-----------------|
|**CrewAI**|0.157.0 (Updated 2025-08-13)|Declarative YAML mission files, vector‑based memory, Agents → Roles → Tasks hierarchy.|
|**Microsoft Autogen**|0.2 (major rewrite) citeturn0search2|Replay analytics, compliance hooks, VS Code debug adapter.|
|**LangGraph**|0.6.4 (Updated 2025-08-13)|Graph‑style branching flows; easy to plug into LangChain tools.|
|**Semantic Kernel**|1.35.0 (Jul 15) citeturn1search7|Process Framework (durable orchestration) + C#/**Python** parity.|
|**GPTScript Agents**|Bleeding‑edge citeturn1search5|Script agents in 10 lines; great for Kubernetes ops.|
|**Clio (CLI Copilot)**|Active citeturn1search8|Executes shell commands safely with confirm step.|

See the ODSC roundup for nine more frameworks citeturn1search2.

---

## 4 · Azure‑centric Agent Tooling  

* **Azure AI Foundry**—“agent factory” announced at Build 2025. Adds governed deployment, Deep Research API (public preview) citeturn1search0turn1search6  
* **Project Amelie**—auto‑builds ML pipelines from one prompt citeturn1search3  

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

(Install custom ISOs if 24.04 hasn’t hit the Store yet citeturn0search7.)

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
|**Azure AI Foundry Blog** | Enterprise agent governance & roadmap citeturn1search0.|

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

This workstation now includes automated weekly updates to keep your AI agent development environment current:

### Automated Update Features

| Component | What it does | Frequency |
|-----------|-------------|-----------|
|**Tool Version Tracking**|Checks PyPI, npm, and GitHub for updates to all tracked frameworks|Weekly|
|**Community Monitoring**|Scans OpenAI forums, GitHub discussions, and Reddit for trending topics|Weekly|
|**Trending Tool Discovery**|Identifies new AI agent tools and frameworks gaining popularity|Weekly|
|**README Auto-Updates**|Updates version numbers and adds new trending tools to this document|Weekly|

### MCP Server Configuration

Your `.vscode/mcp.json` is configured with:
- **Context7** for enhanced AI context management
- **Memory server** for persistent agent sessions
- **Web search** for real-time information access
- **GitHub integration** for repository management
- **Filesystem access** for local development

### Running Updates

```bash
# Manual update (weekly automation recommended)
./scripts/weekly-update.sh

# Check individual components
python3 scripts/update-tools.py
python3 scripts/forum-monitor.py
```

### Setup Automation

```bash
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

# Search API (for web search MCP)
SEARCH_API_KEY=your_google_search_api_key
SEARCH_ENGINE_ID=your_search_engine_id

# GitHub integration
GITHUB_TOKEN=your_github_personal_access_token
```

---

*Generated August 13, 2025 – automatically updating weekly to keep pace with the evolving agentic toolbox.*  


---

## Trending Tools to Investigate

| Tool | Stars | Language | Use Case | Repository |
|------|-------|----------|----------|------------|
|**rag-ecosystem**|89|Jupyter Notebook|Understand and code every important component of RAG architecture|[GitHub](https://github.com/FareedKhan-dev/rag-ecosystem)|
