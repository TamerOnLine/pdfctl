"""
pdfctl/web.py — نقطة دخول لتشغيل واجهة الويب Streamlit
"""

import os
import sys
from pathlib import Path

def main():
    # نحدّد مسار ملف تطبيق Streamlit
    app_path = Path(__file__).resolve().parent / "app.py"

    if not app_path.exists():
        print(f"[error] لم يتم العثور على ملف Streamlit: {app_path}")
        sys.exit(1)

    # تشغيل streamlit عبر execvp (يستبدل العملية الحالية)
    os.execvp("streamlit", ["streamlit", "run", str(app_path)])
