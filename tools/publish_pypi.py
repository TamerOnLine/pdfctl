from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path

from dotenv import load_dotenv

def sh(cmd: list[str], cwd: Path | None = None) -> None:
    """
    Execute a shell command and ensure it completes successfully.

    Args:
        cmd (list[str]): The command to run as a list of arguments.
        cwd (Path | None): The working directory to run the command in.
    """
    print(">", " ".join(cmd))
    subprocess.run(cmd, cwd=cwd, check=True)

def die(msg: str, code: int = 1) -> None:
    """
    Print an error message and exit the script.

    Args:
        msg (str): Error message to print.
        code (int): Exit status code.
    """
    print(f"[ERROR] {msg}")
    raise SystemExit(code)

def mask_token(tok: str) -> str:
    """
    Mask a token for secure display.

    Args:
        tok (str): The token string.

    Returns:
        str: A masked version of the token.
    """
    return tok[:6] + "..." + tok[-4:] if len(tok) > 10 else "********"

def parse_args() -> argparse.Namespace:
    """
    Parse command-line arguments.

    Returns:
        argparse.Namespace: Parsed command-line arguments.
    """
    ap = argparse.ArgumentParser(description="Build & upload package to PyPI/TestPyPI")
    ap.add_argument("--repo", choices=["pypi", "testpypi"], default="pypi")
    ap.add_argument("--skip-build", action="store_true", help="Skip build step")
    ap.add_argument("--clean-dist", action="store_true", help="Remove dist/ before build")
    ap.add_argument("--verbose", action="store_true", help="Verbose upload output")
    return ap.parse_args()

def main() -> int:
    """
    Main function to handle building and uploading a Python package to PyPI or TestPyPI.

    Returns:
        int: Exit code of the operation.
    """
    args = parse_args()
    root = Path(__file__).resolve().parents[1]

    # Load .env file if present
    env_path = root / ".env"
    if env_path.exists():
        load_dotenv(env_path)
        print(f"[info] Loaded .env from {env_path}")
    else:
        print("[warn] No .env file found in project root")

    # Retrieve API token
    token = os.getenv("PYPI_API_TOKEN") or ""
    if not token.startswith("pypi-"):
        die("A valid token was not found in the .env file (must start with pypi-)")

    print(f"[info] Repository: {args.repo}")
    print(f"[info] Token: {mask_token(token)}")

    # Clean dist directory if needed
    dist = root / "dist"
    if args.clean_dist and dist.exists():
        print("[clean] Removing old dist/")
        shutil.rmtree(dist, ignore_errors=True)

    # Build the package
    if not args.skip_build:
        print("[build] Building package...")
        sh([sys.executable, "-m", "build"], cwd=root)
    else:
        print("[build] Skipped (using existing dist/)")

    if not dist.exists() or not any(dist.iterdir()):
        die("dist/ folder is empty. Nothing to upload.")

    # Upload using twine
    print("[upload] Uploading via Twine...")
    cmd = [
        "twine", "upload", "dist/*",
        "-u", "__token__",
        "-p", token,
    ]
    if args.repo == "testpypi":
        cmd.insert(2, "--repository")
        cmd.insert(3, "testpypi")
    if args.verbose:
        cmd.append("--verbose")

    sh(cmd, cwd=root)
    print("[success] Upload finished successfully.")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())