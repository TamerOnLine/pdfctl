"""
runner.py — Launches the Streamlit-based PDFCTL web interface.

This script acts as a lightweight launcher that executes the `web.py`
Streamlit application. It does not enter a runtime loop itself.
"""

from pathlib import Path
import argparse
import os


def main():
    """
    Launch the PDFCTL Streamlit application on a specified port.

    This function locates the `web.py` file in the same directory and
    runs it using Streamlit. The server port can be specified via the
    `--port` argument (default is 8501).

    Args:
        --port (int, optional): Port to run the Streamlit app on. Defaults to 8501.
    """
    parser = argparse.ArgumentParser(description="Run the PDFCTL web interface.")
    parser.add_argument(
        "--port",
        type=int,
        default=8501,
        help="Port to run the Streamlit server on."
    )
    args = parser.parse_args()

    app = Path(__file__).with_name("web.py")  # Points to the main application file
    os.execvp("streamlit", ["streamlit", "run", str(app), "--server.port", str(args.port)])


if __name__ == "__main__":
    main()
