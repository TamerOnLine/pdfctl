# -*- coding: utf-8 -*-
"""
web.py — Streamlit-based web interface for PDFCTL.
Runs the PDF control UI (merge, split, extract, rotate) via Streamlit.
"""

import os
import argparse
from pathlib import Path


def main():
    """
    Launch the Streamlit application with an optional port argument.

    This function sets up and runs the Streamlit server that hosts the PDFCTL
    web interface, which provides tools for managing PDF files such as merging,
    splitting, extracting, and rotating.

    Args:
        --port (int, optional): The port to run the Streamlit server on.
            Defaults to 8501.
    """
    parser = argparse.ArgumentParser(description="Run the PDFCTL web interface.")
    parser.add_argument(
        "--port",
        type=int,
        default=8501,
        help="Port to run the Streamlit server on."
    )
    args = parser.parse_args()

    app_path = Path(__file__).resolve()

    print(f"[info] Starting Streamlit server on port {args.port}...")
    print(f"[info] Launching app: {app_path}")

    # Correct method to start Streamlit (automatically opens in the browser)
    os.execvp("streamlit", ["streamlit", "run", str(app_path), "--server.port", str(args.port)])


if __name__ == "__main__":
    main()
