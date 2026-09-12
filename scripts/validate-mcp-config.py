#!/usr/bin/env python3
"""Validate MCP server configuration and tracking metadata consistency."""

import argparse
import json
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any


MCP_CONFIG_PATH = Path('.vscode/mcp.json')
TRACKING_PATH = Path('config/tools-tracking.json')
PACKAGE_PATH = Path('package.json')
PACKAGE_LOCK_PATH = Path('package-lock.json')
DEPRECATED_ENV_KEYS = {
    'SEARCH_API_KEY',
    'SEARCH_ENGINE_ID',
    # context7 authenticates with CONTEXT7_API_KEY, not Upstash Redis creds.
    'UPSTASH_REDIS_REST_URL',
    'UPSTASH_REDIS_REST_TOKEN',
}


def load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f'Missing required file: {path}')
    return json.loads(path.read_text(encoding='utf-8'))


def extract_npm_package(server_cfg: dict[str, Any]) -> str | None:
    command = server_cfg.get('command')
    args = server_cfg.get('args', [])

    if not isinstance(args, list):
        return None

    if command == 'npx':
        for token in args:
            if isinstance(token, str) and token.startswith('@'):
                return token.rsplit('@', 1)[0] if '@' in token[1:] else token

    if command == 'node' and args and isinstance(args[0], str):
        match = re.fullmatch(
            r'\$\{workspaceFolder\}/node_modules/(@[^/]+/[^/]+|[^/]+)/.+',
            args[0],
        )
        if match:
            return match.group(1)

    return None


def is_secret_reference(value: object, inputs: object) -> bool:
    if not isinstance(value, str):
        return False
    if re.fullmatch(r'\$\{env:[A-Za-z_][A-Za-z0-9_]*\}', value):
        return True
    match = re.fullmatch(r'\$\{input:([^}]+)\}', value)
    if match is None or not isinstance(inputs, list):
        return False
    return any(
        isinstance(item, dict)
        and item.get('id') == match.group(1)
        and item.get('type') == 'promptString'
        and item.get('password') is True
        for item in inputs
    )


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
    package = load_json(PACKAGE_PATH)
    package_lock = load_json(PACKAGE_LOCK_PATH)

    servers = mcp_config.get('servers', {})
    tracked = tracking.get('tracked_tools', {}).get('mcp_servers', {})
    dependencies = package.get('dependencies', {})
    locked_packages = package_lock.get('packages', {})

    if not isinstance(servers, dict):
        print('ERROR: .vscode/mcp.json must contain an object at servers')
        return 1

    if not isinstance(tracked, dict):
        print('ERROR: config/tools-tracking.json missing tracked_tools.mcp_servers')
        return 1

    errors: list[str] = []
    warnings: list[str] = []
    mcp_packages: set[str] = set()

    lock_root = locked_packages.get('') if isinstance(locked_packages, dict) else None
    if (
        not isinstance(dependencies, dict)
        or not isinstance(lock_root, dict)
        or lock_root.get('dependencies') != dependencies
    ):
        errors.append('package.json dependencies must match package-lock.json')

    if isinstance(locked_packages, dict):
        for package_path, lock_entry in locked_packages.items():
            if not package_path:
                continue
            if (
                not isinstance(lock_entry, dict)
                or (
                    lock_entry.get('link') is not True
                    and not isinstance(lock_entry.get('integrity'), str)
                )
            ):
                errors.append(
                    f"Locked package '{package_path}' must include an integrity hash"
                )

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
            if server_cfg.get('command') != 'node':
                errors.append(
                    f"Server '{server_name}' must use its workspace-local locked package"
                )
            if pkg not in tracked:
                errors.append(
                    f"Package '{pkg}' used by server '{server_name}' is not tracked in config/tools-tracking.json"
                )
            version = dependencies.get(pkg) if isinstance(dependencies, dict) else None
            if not isinstance(version, str) or re.fullmatch(r'\d+\.\d+\.\d+', version) is None:
                errors.append(
                    f"Package '{pkg}' must have an exact version in package.json"
                )
            lock_entry = (
                locked_packages.get(f'node_modules/{pkg}')
                if isinstance(locked_packages, dict)
                else None
            )
            if (
                not isinstance(lock_entry, dict)
                or lock_entry.get('version') != version
                or not isinstance(lock_entry.get('integrity'), str)
            ):
                errors.append(
                    f"Package '{pkg}' must match an integrity-pinned package-lock.json entry"
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
        elif server_cfg.get('type') == 'stdio':
            errors.append(
                f"Server '{server_name}' must reference a workspace-local npm package"
            )

    for server_name, key in (
        ('context7', 'CONTEXT7_API_KEY'),
        ('brave-search', 'BRAVE_API_KEY'),
    ):
        config = servers.get(server_name)
        if not isinstance(config, dict):
            continue
        env = config.get('env', {})
        if not isinstance(env, dict):
            errors.append(f"Server '{server_name}' env must be an object")
        elif not is_secret_reference(env.get(key), mcp_config.get('inputs', [])):
            errors.append(
                f"Server '{server_name}' must map {key} to a VS Code "
                "'${env:VARIABLE}' reference or a defined password input"
            )

    filesystem = servers.get('filesystem')
    if isinstance(filesystem, dict):
        args = filesystem.get('args', [])
        if not isinstance(args, list) or '${workspaceFolder}' not in args:
            errors.append("Server 'filesystem' must include '${workspaceFolder}' in args")
        elif '--allowed-directory' in args:
            errors.append(
                "Server 'filesystem' uses positional directories, not '--allowed-directory'"
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
        help='Also verify configured package names exist in npm registry',
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
