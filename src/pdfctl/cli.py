from __future__ import annotations

from pathlib import Path
from typing import Optional, List
import sys

import typer
from rich import print
from rich.console import Console
from pypdf import PdfReader, PdfWriter
from pypdf.generic import NameObject
from pypdf.errors import PdfReadError

from .ranges import parse_ranges

app = typer.Typer(add_completion=False, help="🧰 أدوات التحكم بملفات PDF: دمج، تقسيم، استخراج، تدوير، بيانات، تشفير/فك.")

console = Console()

def _ensure_parent(p: Path):
    p.parent.mkdir(parents=True, exist_ok=True)

def _load_reader(p: Path) -> PdfReader:
    try:
        return PdfReader(str(p))
    except PdfReadError as e:
        console.print(f"[red]فشل قراءة الملف:[/red] {p} — {e}")
        raise typer.Exit(1)

def _write_pdf(writer: PdfWriter, out_path: Path):
    _ensure_parent(out_path)
    with open(out_path, "wb") as f:
        writer.write(f)

@app.command()
def info(pdf: Path):
    """عرض معلومات أساسية عن ملف PDF."""
    r = _load_reader(pdf)
    print(f"[bold]{pdf.name}[/bold]")
    print(f"- الصفحات: {len(r.pages)}")
    if r.metadata:
        print("- البيانات الوصفية:")
        for k, v in r.metadata.items():
            print(f"  • {k}: {v}")

@app.command()
def merge(
    output: Path = typer.Argument(..., help="مسار ملف الإخراج"),
    inputs: List[Path] = typer.Argument(..., help="قائمة ملفات PDF المراد دمجها بالترتيب"),
):
    """دمج عدة ملفات PDF إلى ملف واحد."""
    w = PdfWriter()
    for p in inputs:
        r = _load_reader(p)
        for page in r.pages:
            w.add_page(page)
    _write_pdf(w, output)
    print(f"[green]✔ تم الدمج:[/green] {output}")

@app.command()
def split(
    pdf: Path,
    ranges: str = typer.Argument(..., help='تعبير نطاقات مثل "1-3,5,7-"'),
    output_dir: Path = typer.Option(Path("out"), help="مجلد الإخراج"),
    prefix: str = typer.Option("part", help="بادئة أسماء الملفات"),
):
    """
    تقسيم ملف PDF إلى مقاطع حسب النطاقات.
    كل عنصر في النطاق ينتج ملفًا مستقلًا، مع الحفاظ على ترتيب الصفحات داخل النطاق.
    """
    r = _load_reader(pdf)
    total = len(r.pages)
    # نحول النطاقات إلى كتل (مستمرة) بدل صفحات منفصلة
    # مثال: "1-3,10-12" ⇒ كتلتان
    # إذا أدخل المستخدم صفحات متفرقة (مثلاً "1,3,5") سننتج ملفات صفحة-بصفحة.
    chunks_str = [s.strip() for s in ranges.split(",") if s.strip()]
    _ensure_parent(output_dir)

    for i, chunk in enumerate(chunks_str, start=1):
        pages_idx = parse_ranges(chunk, total_pages=total)
        if not pages_idx:
            continue
        w = PdfWriter()
        for idx in pages_idx:
            if idx < 0 or idx >= total:
                console.print(f"[yellow]تحذير:[/yellow] تجاهل صفحة خارج المدى: {idx+1}")
                continue
            w.add_page(r.pages[idx])
        out = output_dir / f"{prefix}_{i:02d}.pdf"
        _write_pdf(w, out)
        print(f"[green]✔[/green] حفظ: {out}")

@app.command()
def extract(
    pdf: Path,
    pages: str = typer.Argument(..., help='نطاق/صفحات للاستخراج مثل "2,5-7"'),
    output: Path = typer.Option(Path("extracted.pdf"), help="ملف الإخراج"),
):
    """استخراج صفحات محددة إلى ملف جديد."""
    r = _load_reader(pdf)
    idxs = parse_ranges(pages, total_pages=len(r.pages))
    w = PdfWriter()
    for i in idxs:
        w.add_page(r.pages[i])
    _write_pdf(w, output)
    print(f"[green]✔ تم الاستخراج:[/green] {output}")

@app.command()
def rotate(
    pdf: Path,
    pages: str = typer.Argument(..., help='مثال "1-3,7"'),
    angle: int = typer.Option(90, help="درجة التدوير (90/180/270) مع اتجاه عقارب الساعة"),
    output: Path = typer.Option(Path("rotated.pdf")),
):
    """تدوير صفحات محددة."""
    r = _load_reader(pdf)
    w = PdfWriter()
    to_rotate = set(parse_ranges(pages, total_pages=len(r.pages)))
    for i, page in enumerate(r.pages):
        new_page = page
        if i in to_rotate:
            new_page.rotate(angle)
        w.add_page(new_page)
    _write_pdf(w, output)
    print(f"[green]✔ تم التدوير:[/green] {output}")

@app.command()
def meta_show(pdf: Path):
    """عرض البيانات الوصفية (Metadata)."""
    r = _load_reader(pdf)
    for k, v in (r.metadata or {}).items():
        print(f"{k}: {v}")

@app.command()
def meta_set(
    pdf: Path,
    output: Path = typer.Option(Path("meta.pdf")),
    title: Optional[str] = None,
    author: Optional[str] = None,
    subject: Optional[str] = None,
    keywords: Optional[str] = None,
):
    """تعديل البيانات الوصفية الأساسية."""
    r = _load_reader(pdf)
    w = PdfWriter()
    for p in r.pages:
        w.add_page(p)

    info = {}
    if title is not None: info["/Title"] = title
    if author is not None: info["/Author"] = author
    if subject is not None: info["/Subject"] = subject
    if keywords is not None: info["/Keywords"] = keywords
    if info:
        w.add_metadata(info)

    _write_pdf(w, output)
    print(f"[green]✔[/green] حفظ مع Metadata: {output}")

@app.command()
def encrypt(
    pdf: Path,
    output: Path = typer.Option(Path("encrypted.pdf")),
    user_password: str = typer.Option(..., prompt=True, hide_input=True),
    owner_password: str = typer.Option(..., prompt=True, hide_input=True),
    allow_print: bool = typer.Option(True, help="السماح بالطباعة"),
    allow_copy: bool = typer.Option(False, help="السماح بالنسخ"),
    allow_annotate: bool = typer.Option(False, help="السماح بالتعليقات"),
):
    """تشفير PDF بكلمات مرور وصلاحيات بسيطة."""
    r = _load_reader(pdf)
    w = PdfWriter()
    for p in r.pages:
        w.add_page(p)

    perms = set()
    if allow_print:
        perms.add(NameObject("/Print"))
    if allow_copy:
        perms.add(NameObject("/Copy"))
    if allow_annotate:
        perms.add(NameObject("/Annotate"))

    w.encrypt(
        user_password=user_password,
        owner_password=owner_password,
        permissions=perms if perms else None,
    )
    _write_pdf(w, output)
    print(f"[green]✔[/green] تم التشفير: {output}")

@app.command()
def decrypt(
    pdf: Path,
    output: Path = typer.Option(Path("decrypted.pdf")),
    password: str = typer.Option(..., prompt=True, hide_input=True),
):
    """فك تشفير PDF إذا كانت كلمة المرور صحيحة."""
    r = PdfReader(str(pdf))
    if r.is_encrypted:
        if not r.decrypt(password):
            console.print("[red]فشل فك التشفير: كلمة المرور غير صحيحة[/red]")
            raise typer.Exit(1)
    w = PdfWriter()
    for p in r.pages:
        w.add_page(p)
    _write_pdf(w, output)
    print(f"[green]✔[/green] تم فك التشفير: {output}")

if __name__ == "__main__":
    app()
