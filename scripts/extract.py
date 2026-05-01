#!/usr/bin/env python3
"""
Extract text from a PDF file for book-to-skill processing.

Tries extraction methods in order:
  1. pdftotext (poppler-utils) — best quality
  2. PyPDF2 — common Python library
  3. pdfminer.six — thorough fallback

Outputs:
  /tmp/book_skill_work/full_text.txt  — full extracted text
  /tmp/book_skill_work/metadata.json  — stats and metadata
"""

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

OUTPUT_DIR = Path("/tmp/book_skill_work")
OUTPUT_TEXT = OUTPUT_DIR / "full_text.txt"
OUTPUT_META = OUTPUT_DIR / "metadata.json"

WORDS_PER_TOKEN = 0.75  # approximate


def estimate_tokens(text: str) -> int:
    return int(len(text.split()) / WORDS_PER_TOKEN)


def extract_with_pdftotext(pdf_path: str) -> str | None:
    if not shutil.which("pdftotext"):
        return None
    try:
        result = subprocess.run(
            ["pdftotext", "-layout", pdf_path, "-"],
            capture_output=True, text=True, timeout=120
        )
        if result.returncode == 0 and result.stdout.strip():
            return result.stdout
    except Exception:
        pass
    return None


def extract_with_pypdf2(pdf_path: str) -> str | None:
    try:
        import PyPDF2
        text_parts = []
        with open(pdf_path, "rb") as f:
            reader = PyPDF2.PdfReader(f)
            for page in reader.pages:
                try:
                    text_parts.append(page.extract_text() or "")
                except Exception:
                    text_parts.append("")
        return "\n".join(text_parts)
    except ImportError:
        return None
    except Exception:
        return None


def extract_with_pdfminer(pdf_path: str) -> str | None:
    try:
        from pdfminer.high_level import extract_text
        return extract_text(pdf_path)
    except ImportError:
        return None
    except Exception:
        return None


def count_pages(pdf_path: str) -> int:
    # Try pdfinfo first
    if shutil.which("pdfinfo"):
        try:
            result = subprocess.run(
                ["pdfinfo", pdf_path], capture_output=True, text=True, timeout=15
            )
            for line in result.stdout.splitlines():
                if line.startswith("Pages:"):
                    return int(line.split(":")[1].strip())
        except Exception:
            pass
    # Fallback: count form-feed chars (pdftotext -layout uses \f between pages)
    try:
        import PyPDF2
        with open(pdf_path, "rb") as f:
            return len(PyPDF2.PdfReader(f).pages)
    except Exception:
        return 0


def detect_structure(text: str) -> dict:
    """Detect chapter count and table of contents presence."""
    import re
    lines = text[:50000].splitlines()

    # Look for chapter headings
    chapter_pattern = re.compile(
        r"^\s*(chapter\s+\d+|CHAPTER\s+\d+|ch\.\s*\d+|\d+\.\s+[A-Z])",
        re.IGNORECASE
    )
    chapters_found = [l.strip() for l in lines if chapter_pattern.match(l)]

    # Look for ToC indicators
    toc_keywords = ["table of contents", "contents", "índice", "sumário"]
    has_toc = any(kw in text[:5000].lower() for kw in toc_keywords)

    return {
        "chapters_detected": len(chapters_found),
        "chapter_headings_sample": chapters_found[:10],
        "has_toc": has_toc,
    }


def main():
    if len(sys.argv) < 2:
        print("Usage: extract.py <path-to-pdf>", file=sys.stderr)
        sys.exit(1)

    pdf_path = sys.argv[1]

    if not os.path.exists(pdf_path):
        print(f"ERROR: File not found: {pdf_path}", file=sys.stderr)
        sys.exit(1)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    print(f"Extracting: {pdf_path}")
    print("Trying pdftotext...", end=" ", flush=True)
    text = extract_with_pdftotext(pdf_path)

    if text:
        method = "pdftotext"
        print("OK")
    else:
        print("not available")
        print("Trying PyPDF2...", end=" ", flush=True)
        text = extract_with_pypdf2(pdf_path)
        if text:
            method = "PyPDF2"
            print("OK")
        else:
            print("not available")
            print("Trying pdfminer.six...", end=" ", flush=True)
            text = extract_with_pdfminer(pdf_path)
            if text:
                method = "pdfminer"
                print("OK")
            else:
                print("FAILED")
                print(
                    "\nERROR: Could not extract text from PDF.\n"
                    "Install one of: poppler-utils (pdftotext), PyPDF2, or pdfminer.six\n"
                    "  sudo apt install poppler-utils\n"
                    "  pip3 install PyPDF2\n"
                    "  pip3 install pdfminer.six",
                    file=sys.stderr,
                )
                sys.exit(1)

    # Write full text
    OUTPUT_TEXT.write_text(text, encoding="utf-8")

    pages = count_pages(pdf_path)
    tokens = estimate_tokens(text)
    structure = detect_structure(text)
    file_size_mb = os.path.getsize(pdf_path) / (1024 * 1024)

    metadata = {
        "source_file": str(Path(pdf_path).resolve()),
        "filename": Path(pdf_path).name,
        "extraction_method": method,
        "file_size_mb": round(file_size_mb, 2),
        "pages": pages,
        "chars": len(text),
        "words": len(text.split()),
        "estimated_tokens": tokens,
        "estimated_tokens_human": f"~{tokens // 1000}K",
        "output_text": str(OUTPUT_TEXT),
        **structure,
    }

    OUTPUT_META.write_text(json.dumps(metadata, indent=2, ensure_ascii=False))

    print(f"\n📖 Extraction complete:")
    print(f"   Method  : {method}")
    print(f"   Pages   : {pages}")
    print(f"   Words   : {len(text.split()):,}")
    print(f"   Tokens  : ~{tokens // 1000}K")
    print(f"   Chapters: {structure['chapters_detected']} detected")
    print(f"   ToC     : {'yes' if structure['has_toc'] else 'not detected'}")
    print(f"\n   Text → {OUTPUT_TEXT}")
    print(f"   Meta → {OUTPUT_META}")


if __name__ == "__main__":
    main()
