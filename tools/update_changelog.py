from __future__ import annotations

import argparse
import datetime as dt
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PYPROJECT = ROOT / "pyproject.toml"
CHANGELOG = ROOT / "CHANGELOG.md"

def _load_version() -> str:
    """
    Read the version string from pyproject.toml safely.

    Returns:
        str: The extracted version string.

    Raises:
        RuntimeError: If the version field is not found.
    """
    try:
        import tomllib  # Python 3.11+
    except ModuleNotFoundError:
        import tomli as tomllib  # type: ignore[no-redef]

    with PYPROJECT.open("rb") as fp:
        doc = tomllib.load(fp)

    version = (
        doc.get("project", {}).get("version")
        or doc.get("tool", {}).get("poetry", {}).get("version")
    )
    if not version:
        raise RuntimeError("Could not find version in pyproject.toml")
    return str(version)

def _ensure_changelog_exists() -> None:
    """
    Create a basic CHANGELOG.md if it does not already exist.
    """
    if CHANGELOG.exists():
        return

    template = (
        "# Changelog\n\n"
        "All notable changes to this project will be documented in this file.\n"
        "This project follows [Semantic Versioning](https://semver.org/).\n\n"
        "---\n\n"
    )
    CHANGELOG.write_text(template, encoding="utf-8")

def _entry_block(version: str, date_str: str) -> str:
    """
    Create a changelog entry block for a given version and date.

    Args:
        version (str): The version string.
        date_str (str): The date string in ISO format.

    Returns:
        str: Formatted changelog entry block.
    """
    return (
        f"## [{version}] - {date_str}\n"
        "### Added\n"
        "- \n\n"
        "### Changed\n"
        "- \n\n"
        "### Fixed\n"
        "- \n\n"
        "---\n\n"
    )

def _insert_entry_if_missing(version: str) -> bool:
    """
    Insert a new changelog entry if the version is not already listed.

    Args:
        version (str): The version to check and insert.

    Returns:
        bool: True if a new entry was inserted, False otherwise.
    """
    content = CHANGELOG.read_text(encoding="utf-8")

    if re.search(rf"^##\s*\[\s*{re.escape(version)}\s*\]", content, flags=re.M):
        return False

    insert_idx = content.find("\n---")
    if insert_idx != -1:
        insert_idx = content.find("\n", insert_idx + 1) + 1
    else:
        insert_idx = len(content)

    today = dt.date.today().isoformat()
    block = _entry_block(version, today)
    new_content = content[:insert_idx] + block + content[insert_idx:]
    CHANGELOG.write_text(new_content, encoding="utf-8")
    return True

def _run(cmd: list[str], check: bool = True) -> subprocess.CompletedProcess:
    """
    Execute a shell command.

    Args:
        cmd (list[str]): Command and arguments to execute.
        check (bool): Whether to raise on non-zero exit.

    Returns:
        subprocess.CompletedProcess: Result of command execution.
    """
    return subprocess.run(cmd, check=check)

def _git_commit(version: str) -> None:
    """
    Create a git commit for the changelog update.

    Args:
        version (str): The version being committed.
    """
    _run(["git", "add", str(CHANGELOG)])
    _run(["git", "commit", "-m", f"docs: update changelog for v{version}"])

def _git_tag(version: str) -> None:
    """
    Create a git tag for the version.

    Args:
        version (str): The version to tag.
    """
    _run(["git", "tag", f"v{version}"])

def main() -> None:
    """
    Entry point: updates CHANGELOG.md with current version and optionally commits and tags.
    """
    parser = argparse.ArgumentParser(description="Update CHANGELOG from pyproject version.")
    parser.add_argument("--commit", action="store_true", help="Create a git commit for the changelog change.")
    parser.add_argument("--tag", action="store_true", help="Create a git tag vX.Y.Z after updating.")
    args = parser.parse_args()

    if not PYPROJECT.exists():
        raise SystemExit("pyproject.toml not found")

    _ensure_changelog_exists()
    version = _load_version()

    inserted = _insert_entry_if_missing(version)
    if inserted:
        print(f"Added CHANGELOG entry for {version}")
        if args.commit:
            try:
                _git_commit(version)
                print("Created git commit for CHANGELOG update")
            except subprocess.CalledProcessError:
                print("Could not create git commit (is the repo clean and initialized?)")
        if args.tag:
            try:
                _git_tag(version)
                print(f"Created tag v{version}")
            except subprocess.CalledProcessError:
                print("Could not create git tag")
    else:
        print(f"CHANGELOG already contains [{version}] — nothing to do.")

if __name__ == "__main__":
    main()