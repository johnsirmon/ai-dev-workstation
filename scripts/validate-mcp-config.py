#!/usr/bin/env python3
"""Validate MCP server configuration and tracking metadata consistency."""

import argparse
import json
import sys
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any


MCP_CONFIG_PATH = Path('.vscode/mcp.json')
TRACKING_PATH = Path('config/tools-tracking.json')
DEPRECATED_ENV_KEYS = {'SEARCH_API_KEY', 'SEARCH_ENGINE_ID'}


def load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f'Missing required file: {path}')
    return json.loads(path.read_text(encoding='utf-8'))


def extract_npm_package(server_cfg: dict[str, Any]) -> str | None:
    command = server_cfg.get('command')
    args = server_cfg.get('args', [])

    if command != 'npx' or not isinstance(args, list):
        return None

    for token in args:
        if isinstance(token, str) and token.startswith('@'):
            return token
    return None


def check_npm_package_exists(package_name: str, timeout: int = 8) -> bool:
    url = f'https://registry.npmjs.org/{package_name}'
    req = urllib.request.Request(url, headers={'Accept': 'application/json'})

    try:
        with urllib.request.urlopen(req, timeout=timeout) as response:
            return response.status == 200
    except urllib.error.HTTPError as exc:
        if exc.code == 404:
            return False
        raise


def validate(check_registry: bool) -> int:
    mcp_config = load_json(MCP_CONFIG_PATH)
    tracking = load_json(TRACKING_PATH)

    servers = mcp_config.get('servers', {})
    tracked = tracking.get('tracked_tools', {}).get('mcp_servers', {})

    if not isinstance(servers, dict):
        print('ERROR: .vscode/mcp.json must contain an object at servers')
        return 1

    if not isinstance(tracked, dict):
        print('ERROR: config/tools-tracking.json missing tracked_tools.mcp_servers')
        return 1

    errors: list[str] = []
    warnings: list[str] = []
    mcp_packages: set[str] = set()

    for server_name, server_cfg in servers.items():
        if not isinstance(server_cfg, dict):
            errors.append(f"Server '{server_name}' config is not an object")
            continue

        env = server_cfg.get('env', {})
        if isinstance(env, dict):
            deprecated = sorted(set(env.keys()) & DEPRECATED_ENV_KEYS)
            if deprecated:
                errors.append(
                    f"Server '{server_name}' uses deprecated env vars: {', '.join(deprecated)}"
                )

        pkg = extract_npm_package(server_cfg)
        if pkg:
            mcp_packages.add(pkg)
            if pkg not in tracked:
                errors.append(
                    f"Package '{pkg}' used by server '{server_name}' is not tracked in config/tools-tracking.json"
                )
            elif check_registry:
                try:
                    if not check_npm_package_exists(pkg):
                        errors.append(
                            f"Package '{pkg}' (server '{server_name}') does not exist on npm"
                        )
                except Exception as exc:  # noqa: BLE001
                    warnings.append(
                        f"Could not verify npm package '{pkg}': {exc}"
                    )

    brave_cfg = servers.get('brave-search')
    if isinstance(brave_cfg, dict):
        brave_env = brave_cfg.get('env', {})
        if not isinstance(brave_env, dict):
            errors.append("Server 'brave-search' env must be an object")
        elif brave_env.get('BRAVE_API_KEY') != '${BRAVE_API_KEY}':
            errors.append(
                "Server 'brave-search' must map BRAVE_API_KEY to '${BRAVE_API_KEY}'"
            )

    tracked_only = sorted(set(tracked.keys()) - mcp_packages)
    if tracked_only:
        warnings.append(
            'Tracked MCP packages not currently referenced in .vscode/mcp.json: '
            + ', '.join(tracked_only)
        )

    if errors:
        print('MCP validation failed:\n')
        for err in errors:
            print(f'- ERROR: {err}')
        if warnings:
            print('\nWarnings:')
            for warn in warnings:
                print(f'- WARN: {warn}')
        return 1

    print('MCP validation passed.')
    if warnings:
        print('\nWarnings:')
        for warn in warnings:
            print(f'- WARN: {warn}')
    return 0


def main() -> None:
    parser = argparse.ArgumentParser(description='Validate MCP config consistency')
    parser.add_argument(
        '--check-registry',
        action='store_true',
        help='Also verify npx package names exist in npm registry',
    )
    args = parser.parse_args()

    try:
        code = validate(check_registry=args.check_registry)
    except (FileNotFoundError, json.JSONDecodeError, KeyError) as exc:
        print(f'Validation error: {exc}')
        code = 1

    sys.exit(code)


if __name__ == '__main__':
    main()
