import os
import argparse
import streamlit as st

def main():
    """
    Initializes and runs the Streamlit PDF control application.

    Sets up the Streamlit page configuration and displays the title and status.
    Parses command-line arguments to determine the server port.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=8501, help="Port to run the Streamlit app on.")
    args = parser.parse_args()

    st.set_page_config(page_title="PDF Control", layout="wide")
    st.title("PDF Tools — PDFCTL")

    # Display readiness status
    st.write("The application is ready!")

    # Return parsed arguments for external use
    return args

if __name__ == "__main__":
    args = main()
    os.system(f"streamlit run {__file__} --server.port={args.port}")
