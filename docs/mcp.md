# Optional MCP setup

[Back to the guide](../README.md)

You do not need MCP to follow this guide or use a coding agent. The
[starter configuration](../.vscode/mcp.json) is a set of examples, not an installation script.
Start only the servers you trust and need.

## Local servers

1. Open the repository in a **WSL-connected VS Code window**.
2. Install a supported [Node.js LTS release](https://nodejs.org/en/download) in WSL if needed.
   The current Context7 pin requires Node.js 20.18.1 or newer; prefer a supported LTS
   rather than installing an older runtime just to meet that minimum.
3. Run `npm ci --ignore-scripts` from the repository root. This installs the exact dependency
   graph and integrity hashes recorded in `package-lock.json` without running package lifecycle
   scripts.
4. Review each server's package, arguments, and permissions in
   [.vscode/mcp.json](../.vscode/mcp.json).
5. Supply credentials for the servers you want, as described below.
6. Use **MCP: List Servers** to start or disable individual servers and inspect their output.
   Enabling/disabling in VS Code does not require deleting shared configuration.

The starter launches packages from the workspace's `node_modules` directory rather than
downloading code when a server starts. Direct versions are exact in `package.json`, and
`package-lock.json` locks the transitive dependency graph and package integrity hashes.
The lockfile improves reproducibility; it does **not** prove packages are safe. Review lockfile
changes before running `npm ci`, and do not enable blanket tool approvals.

Workspace-configured local servers run in WSL when the workspace is opened through the WSL
extension. User-profile servers may run on the Windows host instead. See
[VS Code's MCP guide](https://code.visualstudio.com/docs/agent-customization/mcp-servers).

## Credentials

The starter uses VS Code's `${env:VARIABLE_NAME}` syntax:

| Server | Server environment variable | VS Code reference |
|---|---|---|
| Context7 | `CONTEXT7_API_KEY` | `${env:CONTEXT7_API_KEY}` |
| Brave Search | `BRAVE_API_KEY` | `${env:BRAVE_API_KEY}` |

Create keys through [Context7](https://context7.com/dashboard) or
[Brave Search](https://api.search.brave.com/), only if using those servers.
Set only the variables each server needs in the environment used to launch the MCP processes.
Local MCP processes can inherit other variables from VS Code, so avoid launching VS Code from
a shell containing unrelated credentials.
Windows and WSL environments are separate; an already-running VS Code Server may not
pick up a later shell export. For remote sessions, follow the official
[WSL server environment setup](https://code.visualstudio.com/docs/remote/wsl#_advanced-environment-setup-script).
Keep credential files outside the workspace where practical, with owner-only permissions.

[.env.example](../.env.example) lists the variable names. A local `.env` is optional:
**VS Code does not automatically load it**, and this repository does not source it.
Do not use `export $(... | xargs)` to parse credential files or source files from untrusted
repositories. A Git-ignored file is still readable by tools that have filesystem access.

For interactive VS Code chat, password-backed input variables are an alternative;
see the [MCP configuration reference](https://code.visualstudio.com/docs/agents/reference/mcp-configuration#_input-variables-for-sensitive-data).
They need matching `inputs` definitions in your configuration. VS Code does not forward
servers requiring interactive inputs to Agent Host sessions, so do not assume that method
works with every agent runtime.

## Filesystem and memory boundaries

- **Filesystem:** the workspace folder is a positional command-line argument. A client that
  supports MCP Roots can replace that initial directory list; inspect the server's
  `list_allowed_directories` result before use. This does not constrain the agent's other
  tools or sandbox the server process.
- **Memory:** the starter writes its persistent graph to `.mcp-memory.jsonl` in the workspace.
  It is Git-ignored, but is not encrypted and can be read by local tools. Store project notes,
  not credentials, personal information, or sensitive conversation transcripts.

## GitHub: bring your own connection

GitHub MCP is deliberately **not included** in the starter. The old
`@modelcontextprotocol/server-github` npm package has been replaced by GitHub's
[official server](https://github.com/github/github-mcp-server).

If needed, add the following entry inside `servers` in your own VS Code MCP configuration:

```json
"github": {
  "type": "http",
  "url": "https://api.githubcopilot.com/mcp/readonly"
}
```

This uses GitHub's hosted read-only toolset and VS Code's sign-in flow; no local npm package,
container, or token committed to a file is needed. Check account/organization policies and
the [official remote-server guide](https://github.com/github/github-mcp-server/blob/main/docs/remote-server.md).
Read-only tools still have access to data your account can read; this is not a substitute
for scoped authorization. Keep write operations and merges separately reviewed.

## Validate changes

From the repository root:

```bash
python3 scripts/validate-mcp-config.py
python3 -m unittest discover -s tests -v
```

When changing packages, update [tools-tracking.json](../config/tools-tracking.json) and the
[README's MCP table](../README.md#optional-tools). Tracking covers npm packages only, not
hosted services or agent frameworks. The optional `--check-registry` flag checks whether
package names exist on npm; it does not audit vulnerabilities. The validator requires exact
direct versions and integrity entries for the complete dependency graph in `package-lock.json`.
