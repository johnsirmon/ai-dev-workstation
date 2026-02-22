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

> **MCP Ecosystem (Jan 2026):** Over 1,000 servers now available. Transport has evolved from local STDIO to **Streamable HTTP** for distributed, cloud-scale deployments. See [blog.modelcontextprotocol.io](https://blog.modelcontextprotocol.io) for the latest spec and server registry.

---

## 2 · Choosing Your Coding Copilot  

| Tool | Strengths | Watch‑outs |
|------|-----------|-----------|
|**GitHub Copilot** (agent mode) | Deep VS Code integration, multi-model sessions, Agent Skills via SKILL.md | Chat context limited to ~16k tokens unless MCP tooling expands it.|
|**Claude Code** extension | 200k+ context, excels at refactors; can share MCP servers. | Must select the **Claude** sidebar; easy to think you’re still in Copilot.|
|**Cursor** | Whole‑file edit commands, great for “make this async”, Agent Mode for autonomous coding.|Adds a separate forked VS Code; ingesting large repos can cause battery drain.|
|**Windsurf** | $15/mo premium AI coding with broad model support including Claude and GPT-5.|Separate IDE fork; may lag behind core VS Code releases.|

### New in VS Code Insiders (Jan–Feb 2026)

| Feature | What it does |
|---------|-------------|
|**Agent Sessions view** | Monitor and manage Copilot, Claude, and background/cloud agents from a single dashboard. Subagents run in parallel for complex workflows.|
|**Copilot Memory** | Remembers relevant context and learnings within a repository (expires after 28 days). Improves code completion and review quality across sessions.|
|**SKILL.md Agent Skills** | Define custom agent capabilities with `SKILL.md` files (invoked as slash commands). Share skills org-wide for consistent team tooling.|
|**Multi-model side-by-side** | Run Anthropic Claude, OpenAI Codex, and GitHub Copilot in the same IDE with shared prompts and tools.|
|**Copilot SDK** (technical preview) | Programmatic access to Copilot for Node.js/TypeScript, Python, Go, and .NET. Enables custom AI platforms and automation pipelines.|
|**Terminal sandboxing** | Prevents agents from executing unsafe commands (macOS/Linux). Auto-approval rules reduce unnecessary prompts while keeping you in control.|

---

## 3 · Leading Agent Frameworks (Feb 2026)

| Framework / Lib | Latest ver. | Killer features |
|-----------------|------------|-----------------|
|**CrewAI**|0.157.0|Declarative YAML mission files, vector‑based memory, Agents → Roles → Tasks hierarchy. Fast multi-agent prototyping.|
|**Microsoft Autogen**|0.7.2|Event-driven multi-agent; human-in-the-loop support. Merging with Semantic Kernel into unified Microsoft Agent Framework (GA Q1 2026).|
|**LangGraph**|1.0 (GA)|**Stable v1.0** reached Oct 2025. Graph‑style state machine orchestration; check-pointing, audit trails. Best for production compliance workloads.|
|**Semantic Kernel**|1.35.2|Enterprise Azure integration, planners, function-calling. Converging with AutoGen into unified Microsoft Agent Framework.|
|**OpenAI Agents SDK**|latest|Official open-source SDK for orchestrating multi-agent workflows; supports handoffs, guardrails, tracing, and the new Responses API (replaces Assistants API by Aug 2026).|
|**smolagents** (HF)|1.24.0|Ultra-minimal Hugging Face agents; CodeAgent paradigm, sandboxed execution, model-agnostic. Great for research/lightweight use.|
|**Agno**|2.5.3|High-performance runtime for large-scale multi-agent systems; streaming, governance, approval workflows, and audit logs built in.|
|**LlamaIndex**|latest|Data/knowledge-centric framework; excels at RAG workflows, document agents, and retrieval-augmented production pipelines.|
|**Google ADK**|latest|Google’s Agent Development Kit with native A2A protocol support; deploy on Cloud Run, GKE, or Vertex AI.|
|**GPTScript Agents**|Bleeding‑edge|Script agents in 10 lines; great for Kubernetes ops.|

### Choosing the Right Framework

| Goal | Best choice |
|------|------------|
|Complex stateful workflows, compliance, audit | **LangGraph** |
|Role-driven multi-agent collaboration | **CrewAI** |
|Enterprise Azure integration, .NET/Java | **Semantic Kernel / AutoGen** |
|OpenAI ecosystem, production agent pipelines | **OpenAI Agents SDK** |
|RAG, document-intensive knowledge workflows | **LlamaIndex** |
|Lightweight research / open-source models | **smolagents** |
|Cross-vendor interoperable agent networks | **Google ADK + A2A** |

---

## 4 · Azure-centric Agent Tooling  

* **Azure AI Foundry**—“agent factory” announced at Build 2025. Adds governed deployment, Deep Research API (public preview)  
* **Azure Functions MCP Support** (GA Jan 2026)—native, secure, scalable hosting for MCP servers with built-in authentication, Streamable HTTP, and Microsoft Entra/OAuth enterprise integration  
* **Project Amelie**—auto‑builds ML pipelines from one prompt  

Integrate via the Azure AI Foundry SDK and MCP:

```bash
pip install azure-ai-foundry
foundry run --config foundry.yaml

# Host your own MCP server on Azure Functions (now GA)
az functionapp create --runtime python --name my-mcp-server ...
```

> **Azure MCP Tip:** Azure Functions MCP support uses on-behalf-of (OBO) authentication so agents access downstream systems with user identity, not shared credentials.

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
|-----------|----------|
|**OpenAI Developer Forum** | Responses API, Agents SDK, and Assistants API deprecation (Aug 2026) updates.|
|**LangChain Slack / Discord** | Rapid Q&A on LangGraph 1.0 templates and production patterns.|
|**Autogen / Semantic Kernel GitHub** | Microsoft unified Agent Framework (GA Q1 2026) design patterns.|
|**Azure AI Foundry Blog** | Enterprise agent governance, Azure Functions MCP, and roadmap.|
|**Hugging Face Discord** | smolagents, open-source models (Llama 4, Qwen 3.5, DeepSeek v4) benchmarks.|
|**MCP Blog** (blog.modelcontextprotocol.io) | Spec updates, new server registry, Streamable HTTP transport.|
|**Google Developer Blog** | A2A protocol upgrades, Agent Development Kit (ADK) releases.|

---

## 8 · 30‑Second Setup Checklist  

- [ ] VS Code Insiders + Copilot Nightly installed  
- [ ] `.vscode/mcp.json` with at least one local server  
- [ ] WSL 2 Ubuntu 24.04 fully upgraded  
- [ ] Docker Desktop with WSL integration ON  
- [ ] `crewAI`, `autogen`, `semantic-kernel` installed in chosen environment  
- [ ] `openai-agents` or `smolagents` installed for agent orchestration  
- [ ] Azure credentials in `az login` & `foundry auth`  
- [ ] Review Copilot Agent Skills (SKILL.md) and enable Copilot Memory in VS Code settings  

> **Done!** You're ready to build and ship multi‑agent apps on your Windows workstation without surprises.

---

## 9 · Key AI Models (Feb 2026)

Knowing which models to reach for is as important as knowing which framework to use.

| Model | Provider | Highlights |
|-------|----------|-----------|
|**GPT-5.x** (5.2/5.3)|OpenAI|Best-in-class reasoning, multimodal, function-calling accuracy. Default for OpenAI Agents SDK.|
|**Claude Opus 4.6 / Sonnet 5**|Anthropic|Opus 4.6 for long-context analytical tasks (200k tokens); Sonnet 5 for coding + creative balance.|
|**Gemini 3 Pro**|Google DeepMind|Advanced multimodal (text/audio/vision), GA Feb 2026 with stable APIs and competitive pricing.|
|**Llama 4**|Meta|Leading open-source choice; ideal for private/local deployments and fine-tuning.|
|**DeepSeek v4 / R1**|DeepSeek|Advanced reasoning, cost-effective self-hosted alternative in open-source AI.|
|**Qwen 3.5**|Alibaba Cloud|Strong multilingual + coding; fast-growing open-source competitor.|

> **Tip:** The OpenAI Assistants API is deprecated in favour of the **Responses API** (announced Mar 2025, sunset Aug 2026). Migrate new projects to the Responses API + Agents SDK stack.

---

## 10 · Agent Interoperability: MCP & A2A

### Model Context Protocol (MCP)

MCP is now the **universal connector** for AI tools and data (“USB for AI”), with 1,000+ available servers and adoption by OpenAI, Google, Microsoft, Hugging Face, and more.

| Update | Details |
|--------|---------|
|**1,000+ server ecosystem** | Servers for databases, REST APIs, IDEs, cloud services, and more.|
|**Streamable HTTP transport** | Replaces early STDIO-only approach; supports millions of requests/day in distributed deployments.|
|**Azure Functions MCP (GA Jan 2026)** | Secure, scalable MCP hosting with built-in Entra/OAuth and OBO authentication.|
|**MCP Registry** | Official server registry for discovery; SDKs for Python, TypeScript, Go, Java.|

### Google Agent2Agent (A2A) Protocol

An open, vendor-neutral standard (now Linux Foundation‑governed) letting agents from any platform discover, authenticate, and collaborate:

```bash
# Each agent publishes a discoverable "agent card"
GET /.well-known/agent.json

# Agents communicate via JSON-RPC 2.0 over HTTPS
# Supports sync results and async task streams
```

| Feature | Details |
|---------|---------|
|**Agent cards** | JSON discovery doc at `/.well-known/agent.json` describing identity and capabilities.|
|**Google ADK** | Open-source Agent Development Kit with native A2A support; deploy on Cloud Run / GKE.|
|**150+ enterprise adopters** | Atlassian, Salesforce, SAP, Shopify, Box, and more.|
|**A2A Inspector** | Web UI for debugging, inspecting, and validating A2A endpoints.|

> **MCP vs A2A:** MCP connects agents to *tools/data*; A2A connects *agents to agents*. Use both for fully interoperable multi-agent systems.

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

*Generated February 22, 2026 - updated by weekly automation or manual runs.*  


---

## Trending Tools to Investigate

| Tool | Stars | Language | Use Case | Repository |
|------|-------|----------|----------|------------|
|**rag-ecosystem**|89|Jupyter Notebook|Understand and code every important component of RAG architecture|[GitHub](https://github.com/FareedKhan-dev/rag-ecosystem)|
