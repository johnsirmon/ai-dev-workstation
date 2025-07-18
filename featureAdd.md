
# Modern AI Agent Development Toolkit — July 18, 2025

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
|**CrewAI**|0.140.0 (Jul 9 2025) citeturn0search1|Declarative YAML mission files, vector‑based memory, Agents → Roles → Tasks hierarchy.|
|**Microsoft Autogen**|0.2 (major rewrite) citeturn0search2|Replay analytics, compliance hooks, VS Code debug adapter.|
|**LangGraph**|Templates & perf boosts citeturn0search3|Graph‑style branching flows; easy to plug into LangChain tools.|
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

*Generated July 18, 2025 – keep exploring; the agentic toolbox grows daily.*  
