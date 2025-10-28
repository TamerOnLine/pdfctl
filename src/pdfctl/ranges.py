from __future__ import annotations

def parse_ranges(expr: str, total_pages: int | None = None) -> list[int]:
    """
    Converts a range expression string into a list of zero-based page indices.

    Example expressions:
        "1-3,5,7-"  => includes pages 1 through 3, 5, and from 7 to the end
        "-4"        => includes pages from the beginning to page 4

    Note:
        - Input pages are 1-based; output indices are 0-based.
        - The total_pages argument is optional and used to extend open-ended ranges.

    Args:
        expr (str): The range expression (e.g., "1-3,5,7-").
        total_pages (int | None, optional): Total number of pages available.

    Returns:
        list[int]: Sorted list of zero-based page indices.

    Raises:
        ValueError: If the expression is empty or contains invalid ranges.
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
                # "-B" => range from 1 to B
                end = int(b)
                if end < 1:
                    raise ValueError("Range end must be >= 1")
                rng = range(1, end + 1)

            elif b == "":
                # "A-" => range from A to total_pages
                start = int(a)
                if start < 1:
                    raise ValueError("Range start must be >= 1")
                if total_pages is None:
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
