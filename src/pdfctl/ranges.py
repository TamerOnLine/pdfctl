from __future__ import annotations

def parse_ranges(expr: str, total_pages: int | None = None) -> list[int]:
    """
    يحول تعبير النطاقات إلى قائمة فهارس صفحات (0-based).
    أمثلة:
      "1-3,5,7-"  => 1..3 و 5 و 7 إلى النهاية
      "-4"        => من البداية حتى 4
    المداخيل صفحات 1-based، الناتج 0-based.

    total_pages اختياري لتمديد النطاق المفتوح للنهاية.
    """
    if not expr:
        raise ValueError("Empty ranges expression.")
    expr = expr.replace(" ", "")
    pages: set[int] = set()
    parts = [p for p in expr.split(",") if p]
    for part in parts:
        if "-" in part:
            a, b = part.split("-", 1)
            a = a.strip()
            b = b.strip()
            if a == "" and b == "":
                raise ValueError("Invalid range: '-'")
            if a == "":
                # -B  => 1..B
                end = int(b)
                if end < 1:
                    raise ValueError("Range end must be >= 1")
                rng = range(1, end + 1)
            elif b == "":
                # A-  => A..total
                start = int(a)
                if start < 1:
                    raise ValueError("Range start must be >= 1")
                if total_pages is None:
                    # سنقرر لاحقًا؛ نخزن كتعليم مفتوح ونوسع لاحقًا إن لزم
                    rng = range(start, (total_pages or start) + 1)
                else:
                    rng = range(start, total_pages + 1)
            else:
                start = int(a)
                end = int(b)
                if start < 1 or end < 1 or end < start:
                    raise ValueError(f"Invalid range: {part}")
                rng = range(start, end + 1)
            for p in rng:
                pages.add(p - 1)
        else:
            p = int(part)
            if p < 1:
                raise ValueError("Page must be >= 1")
            pages.add(p - 1)
    return sorted(pages)
