#!/usr/bin/env python3
"""Update this mirror to the latest alint release on PyPI.

Polls the PyPI JSON API for the newest ``alint`` version. If it is newer than
this mirror's pin, rewrites ``pyproject.toml`` (both the project version and the
``alint==`` dependency), commits, tags ``v<version>``, and pushes. Modeled on
astral-sh/ruff-pre-commit and run by ``.github/workflows/mirror.yml`` on a daily
schedule (and on demand).

Only versions that actually exist on PyPI are tagged, so a pre-commit ``rev``
never points at a version whose wheel is not yet published. Before the first
alint wheel exists, the PyPI lookup 404s and this is a clean no-op.
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
import urllib.request
from pathlib import Path

PYPROJECT = Path(__file__).resolve().parent / "pyproject.toml"
PYPI_JSON = "https://pypi.org/pypi/alint/json"


def latest_pypi_version() -> str | None:
    try:
        req = urllib.request.Request(PYPI_JSON, headers={"Accept": "application/json"})
        with urllib.request.urlopen(req, timeout=30) as r:
            data = json.load(r)
    except Exception as e:  # 404 until the first alint wheel publishes; also transient
        print(f"alint not resolvable on PyPI yet ({e}); nothing to mirror.")
        return None
    version = data.get("info", {}).get("version")
    if not version:
        print("PyPI response had no info.version; nothing to mirror.")
        return None
    return version


def current_pin() -> str | None:
    m = re.search(r'alint==([0-9][^"\']*)', PYPROJECT.read_text())
    return m.group(1) if m else None


def rewrite(version: str) -> None:
    text = PYPROJECT.read_text()
    text = re.sub(r'(alint==)[0-9][^"\']*', rf"\g<1>{version}", text)
    text = re.sub(r'(?m)^version = "[^"]*"', f'version = "{version}"', text, count=1)
    PYPROJECT.write_text(text)


def git(*args: str) -> None:
    subprocess.run(["git", *args], check=True)


def tag_exists(tag: str) -> bool:
    out = subprocess.run(["git", "tag", "--list", tag], capture_output=True, text=True)
    return bool(out.stdout.strip())


def main() -> int:
    latest = latest_pypi_version()
    if latest is None:
        return 0
    if current_pin() == latest and tag_exists(f"v{latest}"):
        print(f"already mirroring alint {latest}; nothing to do.")
        return 0
    print(f"mirroring alint {latest}")
    rewrite(latest)
    git("add", "pyproject.toml")
    # `--allow-empty` guards a re-run where the pin was already bumped but the tag
    # push failed previously (pin unchanged, tag missing).
    git("commit", "--allow-empty", "-m", f"Mirror alint {latest}")
    if not tag_exists(f"v{latest}"):
        git("tag", f"v{latest}")
    git("push", "origin", "HEAD", "--tags")
    print(f"tagged v{latest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
