from pathlib import Path
import streamlit as st
from pypdf import PdfReader, PdfWriter
from pdfctl.ranges import parse_ranges

st.set_page_config(page_title="PDF Control", page_icon="📄", layout="wide")
st.title("📄 PDF Tools — PDFCTL")

tabs = st.tabs(["🔗 Merge", "✂️ Split", "📑 Extract", "🔄 Rotate"])

# ---------- Merge ----------
with tabs[0]:
    st.header("Merge PDF Files")
    uploaded_files = st.file_uploader("Select PDF files", type="pdf", accept_multiple_files=True)
    out_name = st.text_input("Output file name", "merged.pdf")

    if st.button("🚀 Merge Now"):
        if not uploaded_files:
            st.warning("Please upload PDF files to merge.")
        else:
            writer = PdfWriter()
            for f in uploaded_files:
                reader = PdfReader(f)
                for page in reader.pages:
                    writer.add_page(page)

            out_path = Path(out_name)
            with open(out_path, "wb") as f:
                writer.write(f)

            st.success(f"Merge completed: {out_path}")
            st.download_button(
                "⬇️ Download Merged File",
                data=open(out_path, "rb"),
                file_name=out_name
            )

# ---------- Split ----------
with tabs[1]:
    st.header("Split PDF File")
    f = st.file_uploader("Select a PDF file to split", type="pdf", key="split")
    ranges = st.text_input("Ranges", "1-3,4-6,7-")

    if st.button("✂️ Split"):
        if not f:
            st.warning("Please upload a file.")
        else:
            reader = PdfReader(f)
            total = len(reader.pages)
            chunks = [s.strip() for s in ranges.split(",") if s.strip()]
            outputs = []

            for i, chunk in enumerate(chunks, start=1):
                idxs = parse_ranges(chunk, total_pages=total)
                writer = PdfWriter()
                for idx in idxs:
                    writer.add_page(reader.pages[idx])

                out = Path(f"part_{i:02d}.pdf")
                with open(out, "wb") as fo:
                    writer.write(fo)

                outputs.append(out)

            st.success(f"Created {len(outputs)} file(s).")
            for out in outputs:
                st.download_button(
                    f"⬇️ Download {out.name}",
                    data=open(out, "rb"),
                    file_name=out.name
                )

# ---------- Extract ----------
with tabs[2]:
    st.header("Extract Specific Pages")
    f = st.file_uploader("Select a PDF file", type="pdf", key="extract")
    pages = st.text_input("Pages", "2,5-7")

    if st.button("📑 Extract"):
        if not f:
            st.warning("Please upload a file.")
        else:
            reader = PdfReader(f)
            writer = PdfWriter()
            idxs = parse_ranges(pages, total_pages=len(reader.pages))

            for i in idxs:
                writer.add_page(reader.pages[i])

            out = Path("extracted.pdf")
            with open(out, "wb") as fo:
                writer.write(fo)

            st.success("Pages extracted successfully.")
            st.download_button(
                "⬇️ Download Extracted File",
                data=open(out, "rb"),
                file_name="extracted.pdf"
            )

# ---------- Rotate ----------
with tabs[3]:
    st.header("Rotate Specific Pages")
    f = st.file_uploader("Select a PDF file", type="pdf", key="rotate")
    pages = st.text_input("Pages", "1-3")
    angle = st.selectbox("Rotation Angle", [90, 180, 270], index=0)

    if st.button("🔄 Rotate"):
        if not f:
            st.warning("Please upload a file.")
        else:
            reader = PdfReader(f)
            writer = PdfWriter()
            to_rotate = set(parse_ranges(pages, total_pages=len(reader.pages)))

            for i, page in enumerate(reader.pages):
                if i in to_rotate:
                    page.rotate(angle)
                writer.add_page(page)

            out = Path("rotated.pdf")
            with open(out, "wb") as fo:
                writer.write(fo)

            st.success("Pages rotated successfully.")
            st.download_button(
                "⬇️ Download Rotated File",
                data=open(out, "rb"),
                file_name="rotated.pdf"
            )
