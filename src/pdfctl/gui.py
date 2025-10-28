from __future__ import annotations
from pathlib import Path
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

from pypdf import PdfReader, PdfWriter
from pypdf.errors import PdfReadError

# إذا كان ملف ranges.py ضمن نفس الحزمة:
try:
    from .ranges import parse_ranges
except Exception:
    # نسخة بسيطة احتياطية
    def parse_ranges(expr: str, total_pages: int | None = None) -> list[int]:
        expr = expr.replace(" ", "")
        out = set()
        parts = [p for p in expr.split(",") if p]
        for part in parts:
            if "-" in part:
                a, b = part.split("-", 1)
                a, b = a.strip(), b.strip()
                if a == "" and b:
                    end = int(b)
                    rng = range(1, end + 1)
                elif a and b == "":
                    start = int(a)
                    end = total_pages or start
                    rng = range(start, end + 1)
                else:
                    start, end = int(a), int(b)
                    if end < start:
                        raise ValueError("Invalid range")
                    rng = range(start, end + 1)
                for p in rng:
                    out.add(p - 1)
            else:
                p = int(part)
                out.add(p - 1)
        return sorted(out)

# ---------- أدوات مساعدة ----------
def _read_pdf(path: Path) -> PdfReader:
    try:
        return PdfReader(str(path))
    except PdfReadError as e:
        raise RuntimeError(f"فشل قراءة الملف: {path.name} — {e}")

def _write_pdf(w: PdfWriter, out_path: Path):
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "wb") as f:
        w.write(f)

# ---------- الواجهة ----------
class PdfCtlGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("pdfctl — أدوات PDF")
        self.geometry("780x560")
        self.minsize(700, 520)

        nb = ttk.Notebook(self)
        nb.pack(fill="both", expand=True, padx=8, pady=8)

        self.merge_tab = self._build_merge_tab(nb)
        self.split_tab = self._build_split_tab(nb)
        self.extract_tab = self._build_extract_tab(nb)
        self.rotate_tab = self._build_rotate_tab(nb)

        nb.add(self.merge_tab, text="دمج")
        nb.add(self.split_tab, text="تقسيم")
        nb.add(self.extract_tab, text="استخراج")
        nb.add(self.rotate_tab, text="تدوير")

    # -------- دمج --------
    def _build_merge_tab(self, parent):
        frm = ttk.Frame(parent)

        left = ttk.Frame(frm)
        left.pack(side="left", fill="both", expand=True, padx=(0,8), pady=8)

        ttk.Label(left, text="الملفات (بالترتيب):").pack(anchor="w")
        self.lst_merge = tk.Listbox(left, selectmode=tk.EXTENDED)
        self.lst_merge.pack(fill="both", expand=True)

        btns = ttk.Frame(left)
        btns.pack(fill="x", pady=6)
        ttk.Button(btns, text="إضافة ملفات…", command=self._merge_add).pack(side="left")
        ttk.Button(btns, text="إزالة المحدد", command=self._merge_remove).pack(side="left", padx=6)
        ttk.Button(btns, text="أعلى", command=lambda: self._move_selected(self.lst_merge, up=True)).pack(side="left")
        ttk.Button(btns, text="أسفل", command=lambda: self._move_selected(self.lst_merge, up=False)).pack(side="left", padx=6)
        ttk.Button(btns, text="مسح", command=lambda: self.lst_merge.delete(0, tk.END)).pack(side="right")

        right = ttk.LabelFrame(frm, text="الإخراج")
        right.pack(side="left", fill="y", padx=(8,0), pady=8)

        self.var_merge_out = tk.StringVar()
        row = ttk.Frame(right); row.pack(fill="x", padx=8, pady=8)
        ttk.Entry(row, textvariable=self.var_merge_out, width=40).pack(side="left", fill="x", expand=True)
        ttk.Button(row, text="تحديد…", command=self._pick_save_merge).pack(side="left", padx=6)

        ttk.Button(right, text="دمج الآن", command=self._do_merge).pack(padx=8, pady=8, fill="x")

        return frm

    def _merge_add(self):
        paths = filedialog.askopenfilenames(title="اختر ملفات PDF", filetypes=[("PDF","*.pdf")])
        for p in paths:
            self.lst_merge.insert(tk.END, p)

    def _merge_remove(self):
        sel = list(self.lst_merge.curselection())[::-1]
        for i in sel:
            self.lst_merge.delete(i)

    def _pick_save_merge(self):
        p = filedialog.asksaveasfilename(title="ملف الإخراج", defaultextension=".pdf", filetypes=[("PDF","*.pdf")], initialfile="merged.pdf")
        if p:
            self.var_merge_out.set(p)

    def _do_merge(self):
        items = self.lst_merge.get(0, tk.END)
        if not items:
            messagebox.showwarning("تنبيه", "أضف ملفات للدمج.")
            return
        out = self.var_merge_out.get() or filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF","*.pdf")], initialfile="merged.pdf")
        if not out:
            return
        w = PdfWriter()
        try:
            for s in items:
                r = _read_pdf(Path(s))
                for page in r.pages:
                    w.add_page(page)
            _write_pdf(w, Path(out))
            messagebox.showinfo("نجاح", f"تم الدمج: {out}")
        except Exception as e:
            messagebox.showerror("خطأ", str(e))

    # -------- تقسيم --------
    def _build_split_tab(self, parent):
        frm = ttk.Frame(parent, padding=8)

        row1 = ttk.Frame(frm); row1.pack(fill="x")
        ttk.Label(row1, text="الملف:").pack(side="left")
        self.var_split_in = tk.StringVar()
        ttk.Entry(row1, textvariable=self.var_split_in).pack(side="left", fill="x", expand=True, padx=6)
        ttk.Button(row1, text="اختيار…", command=lambda: self._pick_file(self.var_split_in)).pack(side="left")

        row2 = ttk.Frame(frm); row2.pack(fill="x", pady=6)
        ttk.Label(row2, text='النطاقات (مثال: "1-3,10-12,20-")').pack(anchor="w")
        self.var_split_ranges = tk.StringVar(value="1-3,4-6")
        ttk.Entry(row2, textvariable=self.var_split_ranges).pack(fill="x")

        row3 = ttk.Frame(frm); row3.pack(fill="x", pady=6)
        ttk.Label(row3, text="مجلد الإخراج:").pack(side="left")
        self.var_split_outdir = tk.StringVar(value=str(Path("out")))
        ttk.Entry(row3, textvariable=self.var_split_outdir).pack(side="left", fill="x", expand=True, padx=6)
        ttk.Button(row3, text="تحديد…", command=self._pick_dir_split).pack(side="left")

        row4 = ttk.Frame(frm); row4.pack(fill="x", pady=6)
        ttk.Label(row4, text="بادئة الاسم:").pack(side="left")
        self.var_split_prefix = tk.StringVar(value="part")
        ttk.Entry(row4, textvariable=self.var_split_prefix, width=12).pack(side="left", padx=6)

        ttk.Button(frm, text="تقسيم الآن", command=self._do_split).pack(pady=10)

        return frm

    def _pick_file(self, var: tk.StringVar):
        p = filedialog.askopenfilename(title="اختر ملف PDF", filetypes=[("PDF","*.pdf")])
        if p:
            var.set(p)

    def _pick_dir_split(self):
        d = filedialog.askdirectory(title="اختر مجلد الإخراج")
        if d:
            self.var_split_outdir.set(d)

    def _do_split(self):
        src = self.var_split_in.get()
        if not src:
            messagebox.showwarning("تنبيه", "اختر ملفًا للتقسيم.")
            return
        rng = self.var_split_ranges.get().strip()
        if not rng:
            messagebox.showwarning("تنبيه", "أدخل نطاقات.")
            return
        outdir = Path(self.var_split_outdir.get() or "out")
        prefix = self.var_split_prefix.get() or "part"
        try:
            r = _read_pdf(Path(src))
            total = len(r.pages)
            chunks = [s.strip() for s in rng.split(",") if s.strip()]
            outdir.mkdir(parents=True, exist_ok=True)
            count = 0
            for i, chunk in enumerate(chunks, start=1):
                idxs = parse_ranges(chunk, total_pages=total)
                if not idxs:
                    continue
                w = PdfWriter()
                for idx in idxs:
                    if 0 <= idx < total:
                        w.add_page(r.pages[idx])
                out = outdir / f"{prefix}_{i:02d}.pdf"
                _write_pdf(w, out)
                count += 1
            messagebox.showinfo("نجاح", f"تم إنشاء {count} ملف/ملفات في: {outdir}")
        except Exception as e:
            messagebox.showerror("خطأ", str(e))

    # -------- استخراج --------
    def _build_extract_tab(self, parent):
        frm = ttk.Frame(parent, padding=8)

        row1 = ttk.Frame(frm); row1.pack(fill="x")
        ttk.Label(row1, text="الملف:").pack(side="left")
        self.var_ext_in = tk.StringVar()
        ttk.Entry(row1, textvariable=self.var_ext_in).pack(side="left", fill="x", expand=True, padx=6)
        ttk.Button(row1, text="اختيار…", command=lambda: self._pick_file(self.var_ext_in)).pack(side="left")

        row2 = ttk.Frame(frm); row2.pack(fill="x", pady=6)
        ttk.Label(row2, text='الصفحات (مثال: "2,5-7")').pack(anchor="w")
        self.var_ext_pages = tk.StringVar(value="2,5-7")
        ttk.Entry(row2, textvariable=self.var_ext_pages).pack(fill="x")

        row3 = ttk.Frame(frm); row3.pack(fill="x", pady=6)
        ttk.Label(row3, text="ملف الإخراج:").pack(side="left")
        self.var_ext_out = tk.StringVar(value=str(Path("extracted.pdf")))
        ttk.Entry(row3, textvariable=self.var_ext_out).pack(side="left", fill="x", expand=True, padx=6)
        ttk.Button(row3, text="تحديد…", command=lambda: self._pick_save(self.var_ext_out, "extracted.pdf")).pack(side="left")

        ttk.Button(frm, text="استخراج الآن", command=self._do_extract).pack(pady=10)

        return frm

    def _pick_save(self, var: tk.StringVar, default_name: str):
        p = filedialog.asksaveasfilename(title="ملف الإخراج", defaultextension=".pdf",
                                         filetypes=[("PDF","*.pdf")], initialfile=default_name)
        if p:
            var.set(p)

    def _do_extract(self):
        src = self.var_ext_in.get()
        pages = self.var_ext_pages.get().strip()
        out = self.var_ext_out.get() or "extracted.pdf"
        if not src or not pages:
            messagebox.showwarning("تنبيه", "اختر ملفًا وأدخل الصفحات.")
            return
        try:
            r = _read_pdf(Path(src))
            idxs = parse_ranges(pages, total_pages=len(r.pages))
            w = PdfWriter()
            for i in idxs:
                if 0 <= i < len(r.pages):
                    w.add_page(r.pages[i])
            _write_pdf(w, Path(out))
            messagebox.showinfo("نجاح", f"تم الاستخراج: {out}")
        except Exception as e:
            messagebox.showerror("خطأ", str(e))

    # -------- تدوير --------
    def _build_rotate_tab(self, parent):
        frm = ttk.Frame(parent, padding=8)

        row1 = ttk.Frame(frm); row1.pack(fill="x")
        ttk.Label(row1, text="الملف:").pack(side="left")
        self.var_rot_in = tk.StringVar()
        ttk.Entry(row1, textvariable=self.var_rot_in).pack(side="left", fill="x", expand=True, padx=6)
        ttk.Button(row1, text="اختيار…", command=lambda: self._pick_file(self.var_rot_in)).pack(side="left")

        row2 = ttk.Frame(frm); row2.pack(fill="x", pady=6)
        ttk.Label(row2, text='الصفحات (مثال: "1-3,7")').pack(anchor="w")
        self.var_rot_pages = tk.StringVar(value="1-3")
        ttk.Entry(row2, textvariable=self.var_rot_pages).pack(fill="x")

        row3 = ttk.Frame(frm); row3.pack(fill="x", pady=6)
        ttk.Label(row3, text="زاوية التدوير (90/180/270):").pack(side="left")
        self.var_rot_angle = tk.StringVar(value="90")
        ttk.Entry(row3, textvariable=self.var_rot_angle, width=8).pack(side="left", padx=6)

        row4 = ttk.Frame(frm); row4.pack(fill="x", pady=6)
        ttk.Label(row4, text="ملف الإخراج:").pack(side="left")
        self.var_rot_out = tk.StringVar(value=str(Path("rotated.pdf")))
        ttk.Entry(row4, textvariable=self.var_rot_out).pack(side="left", fill="x", expand=True, padx=6)
        ttk.Button(row4, text="تحديد…", command=lambda: self._pick_save(self.var_rot_out, "rotated.pdf")).pack(side="left")

        ttk.Button(frm, text="تدوير الآن", command=self._do_rotate).pack(pady=10)

        return frm

    def _do_rotate(self):
        src = self.var_rot_in.get()
        pages = self.var_rot_pages.get().strip()
        out = self.var_rot_out.get() or "rotated.pdf"
        if not src or not pages:
            messagebox.showwarning("تنبيه", "اختر ملفًا وأدخل الصفحات.")
            return
        try:
            angle = int(self.var_rot_angle.get())
            if angle not in (90,180,270):
                raise ValueError("الزاوية يجب أن تكون 90 أو 180 أو 270.")
            r = _read_pdf(Path(src))
            w = PdfWriter()
            to_rotate = set(parse_ranges(pages, total_pages=len(r.pages)))
            for i, page in enumerate(r.pages):
                pg = page
                if i in to_rotate:
                    pg.rotate(angle)
                w.add_page(pg)
            _write_pdf(w, Path(out))
            messagebox.showinfo("نجاح", f"تم التدوير: {out}")
        except Exception as e:
            messagebox.showerror("خطأ", str(e))

def main():
    app = PdfCtlGUI()
    app.mainloop()

if __name__ == "__main__":
    main()
