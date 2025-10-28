"""
web.py - Entry point for launching the Streamlit web interface.
"""

import os
import sys
from pathlib import Path

def main():
    """
    Launches the Streamlit application by locating 'app.py' and executing it.

    Raises:
        SystemExit: If 'app.py' is not found in the expected directory.
    """
    app_path = Path(__file__).resolve().parent / "app.py"

    if not app_path.exists():
        print(f"[error] Streamlit file not found: {app_path}")
        sys.exit(1)

    os.execvp("streamlit", ["streamlit", "run", str(app_path)])
