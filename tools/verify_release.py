from pathlib import Path
import re
import sys

def extract_version_from_pyproject() -> str:
    """
    Extracts the version string from the pyproject.toml file.

    Returns:
        str: The version string.

    Raises:
        SystemExit: If version is not found.
    """
    py_content = Path("pyproject.toml").read_text(encoding="utf-8")
    match = re.search(r'(?m)^version\s*=\s*"([^"]+)"', py_content)
    if not match:
        print("Error: Version not found in pyproject.toml")
        sys.exit(1)
    return match.group(1)

def check_changelog_for_version(version: str) -> None:
    """
    Verifies that CHANGELOG.md contains a section for the given version.

    Args:
        version (str): The version to verify.

    Raises:
        SystemExit: If the version section is missing.
    """
    changelog = Path("CHANGELOG.md").read_text(encoding="utf-8")
    if not re.search(rf'(?m)^##\s*\[\s*{re.escape(version)}\s*\]', changelog):
        print(f"Error: CHANGELOG.md has no section for [{version}]")
        sys.exit(1)

    block = re.findall(rf'(?s)^##\s*\[\s*{re.escape(version)}\s*\](.+?)(^##\s*\[|\Z)', changelog)
    if not block or all("- " not in line for line in block[0][0].splitlines()):
        print(f"Warning: CHANGELOG section for [{version}] appears empty (no bullet items).")

def main() -> None:
    """
    Main function to verify if the current version in pyproject.toml
    has a corresponding non-empty section in CHANGELOG.md.
    """
    version = extract_version_from_pyproject()
    check_changelog_for_version(version)
    print(f"Ready to tag v{version}")

if __name__ == "__main__":
    main()
