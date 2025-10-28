# run_tests_if_present.py
import os, sys, subprocess
if os.path.isdir("tests"):
    sys.exit(subprocess.call([sys.executable, "-m", "unittest", "discover", "-s", "tests", "-t", "."]))
else:
    print("No tests/ directory; skipping.")
