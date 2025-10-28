from pathlib import Path
import streamlit as st
from pypdf import PdfReader, PdfWriter
from pdfctl.ranges import parse_ranges

st.set_page_config(page_title="PDF Control", page_icon="📄", layout="wide")
st.title("📄 أدوات PDF — PDFCTL")

tabs = st.tabs(["🔗 دمج", "✂️ تقسيم", "📑 استخراج", "🔄 تدوير"])

# ---------- دمج ----------
with tabs[0]:
    st.header("دمج ملفات PDF")
    uploaded_files = st.file_uploader("اختر ملفات PDF", type="pdf", accept_multiple_files=True)
    out_name = st.text_input("اسم ملف الإخراج", "merged.pdf")
    if st.button("🚀 دمج الآن"):
        if not uploaded_files:
            st.warning("الرجاء رفع ملفات للدمج.")
        else:
            writer = PdfWriter()
            for f in uploaded_files:
                reader = PdfReader(f)
                for page in reader.pages:
                    writer.add_page(page)
            out_path = Path(out_name)
            with open(out_path, "wb") as f:
                writer.write(f)
            st.success(f"تم الدمج: {out_path}")
            st.download_button("⬇️ تحميل الملف المدموج", data=open(out_path, "rb"), file_name=out_name)

# ---------- تقسيم ----------
with tabs[1]:
    st.header("تقسيم ملف PDF")
    f = st.file_uploader("اختر ملف PDF للتقسيم", type="pdf", key="split")
    ranges = st.text_input("النطاقات", "1-3,4-6,7-")
    if st.button("✂️ تقسيم"):
        if not f:
            st.warning("الرجاء رفع ملف.")
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
            st.success(f"تم إنشاء {len(outputs)} ملفًا.")
            for out in outputs:
                st.download_button(f"⬇️ تحميل {out.name}", data=open(out, "rb"), file_name=out.name)

# ---------- استخراج ----------
with tabs[2]:
    st.header("استخراج صفحات محددة")
    f = st.file_uploader("اختر ملف PDF", type="pdf", key="extract")
    pages = st.text_input("الصفحات", "2,5-7")
    if st.button("📑 استخراج"):
        if not f:
            st.warning("الرجاء رفع ملف.")
        else:
            reader = PdfReader(f)
            writer = PdfWriter()
            idxs = parse_ranges(pages, total_pages=len(reader.pages))
            for i in idxs:
                writer.add_page(reader.pages[i])
            out = Path("extracted.pdf")
            with open(out, "wb") as fo:
                writer.write(fo)
            st.success("تم الاستخراج.")
            st.download_button("⬇️ تحميل الملف", data=open(out, "rb"), file_name="extracted.pdf")

# ---------- تدوير ----------
with tabs[3]:
    st.header("تدوير صفحات محددة")
    f = st.file_uploader("اختر ملف PDF", type="pdf", key="rotate")
    pages = st.text_input("الصفحات", "1-3")
    angle = st.selectbox("زاوية التدوير", [90, 180, 270], index=0)
    if st.button("🔄 تدوير"):
        if not f:
            st.warning("الرجاء رفع ملف.")
        else:
            reader = PdfReader(f)
            writer = PdfWriter()
            to_rotate = set(parse_ranges(pages, total_pages=len(reader.pages)))
            for i, page in enumerate(reader.pages):
                new_page = page
                if i in to_rotate:
                    new_page.rotate(angle)
                writer.add_page(new_page)
            out = Path("rotated.pdf")
            with open(out, "wb") as fo:
                writer.write(fo)
            st.success("تم التدوير.")
            st.download_button("⬇️ تحميل الملف", data=open(out, "rb"), file_name="rotated.pdf")
