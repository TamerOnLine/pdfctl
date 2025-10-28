# -*- coding: utf-8 -*-
"""
web.py — Streamlit launcher for PDFCTL
--------------------------------------
Launches the main Streamlit application (app.py) that powers the PDFCTL web interface.

Usage:
    python web.py --port 8501
"""

import os
import argparse
from pathlib import Path


def main():
    """
    Launch the Streamlit server for the PDFCTL application.

    This function locates the `app.py` file in the same directory and launches it
    using Streamlit. It accepts an optional `--port` argument to define the port
    number on which the server runs.

    Args:
        --port (int, optional): Port to run the Streamlit app on. Defaults to 8501.
    """
    parser = argparse.ArgumentParser(description="Run the PDFCTL web interface.")
    parser.add_argument(
        "--port",
        type=int,
        default=8501,
        help="Port number to run the Streamlit server on (default: 8501)."
    )
    args = parser.parse_args()

    app_path = Path(__file__).with_name("app.py").resolve()
    print(f"[info] Starting Streamlit server on port {args.port}...")
    print(f"[info] Launching app: {app_path}")

    # Start the Streamlit server for the app.py application
    os.execvp("streamlit", ["streamlit", "run", str(app_path), "--server.port", str(args.port)])


if __name__ == "__main__":
    main()
