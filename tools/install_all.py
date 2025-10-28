# install_all.py
from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import List, Tuple

# -----------------------------
# Utilities
# -----------------------------
def run(cmd: List[str]) -> int:
    print(">", " ".join(cmd))
    return subprocess.call(cmd)

def is_windows() -> bool:
    return os.name == "nt"

def unique_keep_order(items: List[str]) -> List[str]:
    seen = set()
    out = []
    for x in items:
        if x not in seen:
            out.append(x)
            seen.add(x)
    return out

# -----------------------------
# Windows-specific discovery
# -----------------------------
def find_with_py_launcher_flags() -> List[str]:
    """
    Returns py-launcher flags like ['-3.13','-3.12'] using `py -0p`.
    Windows only.
    """
    if not shutil.which("py"):
        return []
    try:
        out = subprocess.check_output(["py", "-0p"], text=True, errors="ignore")
        vers = re.findall(r"(-\d+\.\d+)\s+", out)
        return sorted(set(vers), reverse=True)
    except Exception:
        return []

def find_versions_from_registry() -> List[str]:
    """
    Returns version flags ['-3.13','-3.12'] by looking into Windows Registry.
    Windows only.
    """
    try:
        import winreg  # type: ignore
    except Exception:
        return []

    keys = [
        (getattr(__import__("winreg"), "HKEY_CURRENT_USER"), r"Software\Python\PythonCore"),
        (getattr(__import__("winreg"), "HKEY_LOCAL_MACHINE"), r"Software\Python\PythonCore"),
        (getattr(__import__("winreg"), "HKEY_LOCAL_MACHINE"), r"Software\WOW6432Node\Python\PythonCore"),
    ]
    vers = set()
    for hive, base in keys:
        try:
            with __import__("winreg").OpenKey(hive, base) as k:
                i = 0
                while True:
                    try:
                        sub = __import__("winreg").EnumKey(k, i)
                        i += 1
                        # keep only x.y
                        if re.fullmatch(r"\d+\.\d+", sub):
                            vers.add(f"-{sub}")
                    except OSError:
                        break
        except OSError:
            pass
    return sorted(vers, reverse=True)

def detect_windows_interpreters(ver_opt: str | None) -> List[List[str]]:
    """
    Return list of interpreter "prefix commands" for Windows, e.g.:
        [["py","-3.13"], ["py","-3.12"]]
    If ver_opt provided, it may be "-3.13,3.12" or "all".
    """
    # Normalize input versions to py flags
    def to_py_flag(v: str) -> str:
        v = v.strip()
        if re.fullmatch(r"-?\d+\.\d+", v):
            return v if v.startswith("-") else f"-{v}"
        return v  # path or invalid; handled below

    flags: List[str] = []
    if ver_opt is None or ver_opt.strip().lower() == "all":
        flags = find_with_py_launcher_flags()
        if not flags:
            print("[info] `py -0p` returned nothing; checking Windows registry…")
            flags = find_versions_from_registry()
        if not flags:
            print("[ERROR] No Python versions detected on Windows.")
            return []
    else:
        parts = [p for p in (ver_opt or "").split(",") if p.strip()]
        norm = [to_py_flag(p) for p in parts]
        # Keep only flags that py understands; allow absolute python.exe paths too
        ok: List[str] = []
        for x in norm:
            if x.startswith("-"):
                try:
                    subprocess.check_output(["py", x, "-V"], text=True, stderr=subprocess.STDOUT)
                    ok.append(x)
                except Exception:
                    print(f"[warn] Skipping {x}: interpreter not found by py launcher.")
            else:
                # Treat as a path to python.exe
                if Path(x).exists():
                    ok.append(x)
                else:
                    print(f"[warn] Skipping {x}: not a valid path.")
        flags = ok

    # Build interpreter command prefixes
    interpreters: List[List[str]] = []
    for f in flags:
        if f.startswith("-"):
            interpreters.append(["py", f])
        else:
            # Specific path to python.exe
            interpreters.append([f])
    return interpreters

# -----------------------------
# POSIX (macOS/Linux) discovery
# -----------------------------
COMMON_MINOR_VERS = [f"3.{m}" for m in range(6, 18)][::-1]  # 3.17 .. 3.6 (reverse pref: newer first)

def which_python(name: str) -> str | None:
    p = shutil.which(name)
    return p

def validate_interpreter(cmd: List[str]) -> bool:
    try:
        subprocess.check_output(cmd + ["-c", "import sys;print(sys.version)"], text=True, stderr=subprocess.STDOUT)
        return True
    except Exception:
        return False

def detect_posix_interpreters(ver_opt: str | None) -> List[List[str]]:
    """
    Return list of interpreter command prefixes on macOS/Linux, e.g.:
        [["/usr/bin/python3.13"], ["/usr/local/bin/python3.12"], ["python3"]]
    Strategy:
      - If ver_opt is "all"/None: collect python3.X present on PATH + python3.
      - If ver_opt provided: accept items like "3.13", "python3.13", "python3", or an absolute path.
    """
    found: List[str] = []

    def add_if_exists(name_or_path: str) -> None:
        # If absolute/relative path provided
        if os.sep in name_or_path or name_or_path.startswith("."):
            if Path(name_or_path).exists():
                found.append(str(Path(name_or_path).resolve()))
            return
        # else a command name
        p = which_python(name_or_path)
        if p:
            found.append(p)

    if ver_opt is None or ver_opt.strip().lower() == "all":
        # Try specific python3.X first (prefer newer)
        for v in COMMON_MINOR_VERS:
            add_if_exists(f"python{v}")
            add_if_exists(f"python{v.replace('3.', '3')}")
            add_if_exists(f"python3.{v.split('.')[1]}")
        # Fallback to general python3
        add_if_exists("python3")
        # As a last resort, add "python" if it's actually py3
        p = which_python("python")
        if p:
            try:
                out = subprocess.check_output([p, "-c", "import sys;print(sys.version_info[0])"], text=True)
                if out.strip() == "3":
                    found.append(p)
            except Exception:
                pass
    else:
        parts = [p.strip() for p in ver_opt.split(",") if p.strip()]
        for item in parts:
            if re.fullmatch(r"\d+\.\d+", item):           # e.g. "3.13"
                add_if_exists(f"python{item}")
            elif item.startswith("python"):
                add_if_exists(item)                        # e.g. "python3.12" or "python3"
            else:
                add_if_exists(item)                        # path or name

    # Deduplicate and validate
    found = unique_keep_order(found)
    interpreters: List[List[str]] = []
    for exe in found:
        if validate_interpreter([exe]):
            interpreters.append([exe])
        else:
            print(f"[warn] Skipping invalid interpreter: {exe}")
    return interpreters

# -----------------------------
# Common: load packages
# -----------------------------
def load_packages(json_path: Path) -> List[str]:
    if not json_path.exists():
        print(f"[ERROR] JSON file not found: {json_path}")
        print('Example:\n{\n  "packages": ["reposmith-tol", "fastapi", "uvicorn"]\n}')
        raise SystemExit(1)
    try:
        data = json.loads(json_path.read_text(encoding="utf-8"))
        pkgs = [p.strip() for p in data.get("packages", []) if p.strip()]
    except json.JSONDecodeError as e:
        print(f"[ERROR] Invalid JSON: {e}")
        raise SystemExit(1)
    if not pkgs:
        print("[WARN] No packages listed in packages.json → nothing to do.")
        raise SystemExit(0)
    return pkgs

# -----------------------------
# Main
# -----------------------------
def main() -> int:
    args = sys.argv[1:]
    uninstall = any(a in ("--uninstall", "-u") for a in args)
    dry = "--dry-run" in args

    ver_opt = None
    if "--versions" in args:
        i = args.index("--versions")
        if i + 1 >= len(args):
            print('[ERROR] --versions requires a value, e.g. "-3.13,-3.12" (Windows) or "3.13,3.12" (macOS/Linux) or "all"')
            return 1
        ver_opt = args[i + 1]

    root = Path(__file__).resolve().parent
    packages = load_packages(root / "packages.json")

    # Detect interpreters per OS
    if is_windows():
        interpreters = detect_windows_interpreters(ver_opt)
    else:
        interpreters = detect_posix_interpreters(ver_opt)

    if not interpreters:
        print("[ERROR] No valid Python interpreters were found.")
        return 1

    action = "UNINSTALL" if uninstall else "INSTALL/UPGRADE"
    print(f"Detected interpreters: {interpreters}")
    print(f"Packages: {packages}")
    print(f"Action: {action}{' (dry-run)' if dry else ''}")

    total_ops = 0
    ok_ops = 0

    for interp in interpreters:
        # Display friendly name
        try:
            name = subprocess.check_output(interp + ["-c", "import sys,platform;print(sys.executable)"], text=True).strip()
        except Exception:
            name = " ".join(interp)
        print(f"\n>>> Python @ {name}")
        for pkg in packages:
            total_ops += 1
            cmd = interp + ["-m", "pip", "uninstall", "-y", pkg] if uninstall else interp + ["-m", "pip", "install", "-U", pkg]
            if dry:
                print("DRY:", " ".join(cmd))
                ok_ops += 1
                continue
            rc = run(cmd)
            if rc == 0:
                ok_ops += 1

    print(f"\nDone. Successful operations: {ok_ops}/{total_ops}")
    return 0 if ok_ops == total_ops else 1

if __name__ == "__main__":
    raise SystemExit(main())
