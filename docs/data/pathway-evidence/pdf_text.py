#!/usr/bin/env python3
"""Plain text from a library PDF, for quote extraction and quote checking alike.

    pipeline/.venv/bin/python docs/data/pathway-evidence/pdf_text.py <pdf> [out.txt]

Joins words hyphenated across line ends ("de-\nscribed" -> "described") and collapses whitespace,
so a quote copied from the output will also be found by verify_quotes.py, which reads the same text.
The output goes under verification/cache/local/ (gitignored: third-party full text).
"""
import logging
import re
import sys
from pathlib import Path

logging.getLogger("pypdf").setLevel(logging.ERROR)
from pypdf import PdfReader  # noqa: E402

HERE = Path(__file__).parent
LOCAL = HERE / "verification" / "cache" / "local"


def pdf_to_text(pdf: Path) -> str:
    pages = []
    for i, page in enumerate(PdfReader(str(pdf)).pages, 1):
        t = page.extract_text() or ""
        t = re.sub(r"(\w)-\n(\w)", r"\1\2", t)      # hyphenated line breaks
        t = re.sub(r"\s*\n\s*", " ", t)              # remaining line breaks
        t = t.replace("ﬁ", "fi").replace("ﬂ", "fl").replace("ﬀ", "ff").replace("ﬃ", "ffi").replace("ﬄ", "ffl")
        pages.append(f"\n\n[[page {i}]]\n" + " ".join(t.split()))
    return "".join(pages)


def text_path(pdf: Path) -> Path:
    LOCAL.mkdir(parents=True, exist_ok=True)
    return LOCAL / (pdf.stem + ".txt")


if __name__ == "__main__":
    src = Path(sys.argv[1]).expanduser()
    out = Path(sys.argv[2]) if len(sys.argv) > 2 else text_path(src)
    text = pdf_to_text(src)
    out.write_text(text, encoding="utf-8")
    print(out, len(text), "chars")
