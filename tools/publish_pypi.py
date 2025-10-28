# tools/publish_pypi.py
# -*- coding: utf-8 -*-
"""
نشر تلقائي إلى PyPI أو TestPyPI مع قراءة التوكن من ملف .env في الجذر.
يمكن تشغيله هكذا:
    py -m tools.publish_pypi --repo pypi
أو:
    py -m tools.publish_pypi --repo testpypi

المتطلبات:
    pip install build twine python-dotenv
"""

from __future__ import annotations
import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path
from dotenv import load_dotenv  # ← مكتبة python-dotenv

def sh(cmd: list[str], cwd: Path | None = None) -> None:
    print(">", " ".join(cmd))
    subprocess.run(cmd, cwd=cwd, check=True)

def die(msg: str, code: int = 1) -> None:
    print(f"[ERROR] {msg}")
    raise SystemExit(code)

def mask_token(tok: str) -> str:
    return tok[:6] + "..." + tok[-4:] if len(tok) > 10 else "********"

def parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser(description="Build & upload package to PyPI/TestPyPI")
    ap.add_argument("--repo", choices=["pypi", "testpypi"], default="pypi")
    ap.add_argument("--skip-build", action="store_true", help="Skip build step")
    ap.add_argument("--clean-dist", action="store_true", help="Remove dist/ before build")
    ap.add_argument("--verbose", action="store_true", help="Verbose upload output")
    return ap.parse_args()

def main() -> int:
    args = parse_args()
    root = Path(__file__).resolve().parents[1]

    # 1️⃣ تحميل .env
    env_path = root / ".env"
    if env_path.exists():
        load_dotenv(env_path)
        print(f"[info] Loaded .env from {env_path}")
    else:
        print("[warn] No .env file found in project root")

    # 2️⃣ الحصول على التوكن
    token = os.getenv("PYPI_API_TOKEN") or ""
    if not token.startswith("pypi-"):
        die("❌ لم يتم العثور على توكن صالح في .env (يجب أن يبدأ بـ pypi-)")

    print(f"[info] Repository: {args.repo}")
    print(f"[info] Token: {mask_token(token)}")

    # 3️⃣ بناء الحزمة
    dist = root / "dist"
    if args.clean_dist and dist.exists():
        print("[clean] Removing old dist/")
        shutil.rmtree(dist, ignore_errors=True)

    if not args.skip_build:
        print("[build] Building package...")
        sh([sys.executable, "-m", "build"], cwd=root)
    else:
        print("[build] Skipped (using existing dist/)")

    if not dist.exists() or not any(dist.iterdir()):
        die("dist/ folder is empty. Nothing to upload.")

    # 4️⃣ رفع إلى PyPI
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
    print("[✅] Upload finished successfully.")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())

# py -m tools.publish_pypi --repo pypi
