#!/usr/bin/env python3
"""
Validate and print versions of tracked frameworks from
config/tools-tracking.json. Optionally install/upgrade them in the
current environment with --install.
"""

import argparse
import importlib
import subprocess
import sys
from typing import List

from utils import ConfigManager, Logger


def pip_install(packages: List[str]) -> int:
    cmd = [sys.executable, "-m", "pip", "install"] + packages
    return subprocess.call(cmd)


def main() -> None:
    Logger.setup_logging("INFO")
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--install",
        action="store_true",
        help=(
            "Install/upgrade tracked Python packages to the recorded "
            "versions"
        )
    )
    args = parser.parse_args()

    cfg = ConfigManager().config
    frameworks = cfg["tracked_tools"]["ai_frameworks"]

    python_pkgs = []
    print("Tracked frameworks and target versions:\n")
    for name, meta in frameworks.items():
        target = meta.get("current_version")
        pypi = meta.get("pypi_package")
        print(f"- {name}: {target} ({pypi or 'non-PyPI'})")
        if args.install and pypi:
            python_pkgs.append(f"{pypi}=={target}")

    if args.install and python_pkgs:
        print("\nInstalling/upgrading packages...\n")
        rc = pip_install(python_pkgs)
        if rc != 0:
            print("pip failed; aborting.")
            sys.exit(rc)

    print("\nResolved installed versions:\n")
    for name, meta in frameworks.items():
        pypi = meta.get("pypi_package")
        if not pypi:
            continue
        try:
            mod = importlib.import_module(pypi.replace('-', '_'))
            ver = getattr(mod, "__version__", "unknown")
            print(f"- {name}: {ver} (package: {pypi})")
        except (ImportError, AttributeError) as err:
            print(f"- {name}: not installed ({pypi}) - {err}")


if __name__ == "__main__":
    main()
