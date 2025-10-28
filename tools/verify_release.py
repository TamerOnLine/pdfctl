# verify_release.py
from pathlib import Path
import re, sys

py = Path("pyproject.toml").read_text(encoding="utf-8")
m = re.search(r'(?m)^version\s*=\s*"([^"]+)"', py)
if not m:
    print("❌ version not found in pyproject.toml"); sys.exit(1)
ver = m.group(1)

ch = Path("CHANGELOG.md").read_text(encoding="utf-8")
if not re.search(rf'(?m)^##\s*\[\s*{re.escape(ver)}\s*\]', ch):
    print(f"❌ CHANGELOG.md has no section for [{ver}]"); sys.exit(1)

block = re.findall(rf'(?s)^##\s*\[\s*{re.escape(ver)}\s*\](.+?)(^##\s*\[|\Z)', ch)
if not block or all("- " not in line for line in block[0][0].splitlines()):
    print(f"⚠️ CHANGELOG section for [{ver}] looks empty (no bullet items).")

print(f"✓ Ready to tag v{ver}")
