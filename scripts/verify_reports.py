"""Validate every contact destination and create local PDF contact sheets for visual review."""
from pathlib import Path
import subprocess
import sys

import pymupdf as fitz
from PIL import Image, ImageDraw
from pypdf import PdfReader

ROOT = Path(__file__).resolve().parents[1]
LINKS = {"https://alirezaaies.github.io/", "https://github.com/alirezaaies",
         "https://www.linkedin.com/in/alirezakhajehvandi", "https://www.youtube.com/@AlirezaAIES",
         "https://t.me/AlirezaAIES", "https://www.instagram.com/alireza.aies"}


def verify(language):
    folder = ROOT / "docs" / language
    pdf = folder / "main_report.pdf"
    images = folder / "images"
    images.mkdir(exist_ok=True)
    reader = PdfReader(pdf)
    for index, page in enumerate(reader.pages, 1):
        uris = {str(annotation.get_object().get("/A", {}).get("/URI", ""))
                for annotation in page.get("/Annots", [])}
        if not LINKS <= uris:
            raise ValueError(f"{language} page {index} lacks a required author contact URL.")
        if len(page.extract_text().strip()) < 10:
            raise ValueError(f"{language} page {index} appears blank.")
    doc = fitz.open(pdf)
    outside = []
    for index, page in enumerate(doc, 1):
        width, height = page.rect.width, page.rect.height
        for block in page.get_text("dict")["blocks"]:
            if "lines" not in block:
                continue
            for line in block["lines"]:
                for span in line["spans"]:
                    x0, y0, x1, y1 = span["bbox"]
                    if x0 < 57 or x1 > width - 57 or y0 < 25 or y1 > height - 25:
                        outside.append((index, span["text"][:30]))
    if outside:
        raise ValueError(f"{language}: text outside review bounds on {len(outside)} spans: {outside[:8]}")
    # Render with the required Poppler workflow; these PNGs are never committed.
    for pattern in ("page-*.png", "sheet-*.png"):
        for old in images.glob(pattern):
            old.unlink()
    rendered = subprocess.run(["pdftoppm", "-r", "65", "-png", str(pdf), str(images / "page")],
                              stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=180)
    if rendered.returncode:
        raise RuntimeError(rendered.stderr.decode("utf-8", errors="replace")[:2000])
    pages = sorted(images.glob("page-*.png"), key=lambda p: int(p.stem.split("-")[-1]))
    for start in range(0, len(pages), 12):
        sheet = Image.new("RGB", (1260, 2500), "#dddddd")
        draw = ImageDraw.Draw(sheet)
        for offset, path in enumerate(pages[start:start + 12]):
            preview = Image.open(path).convert("RGB")
            preview.thumbnail((405, 580))
            x = (offset % 3) * 420 + 8
            y = (offset // 3) * 625 + 22
            sheet.paste(preview, (x, y))
            draw.text((x, y - 18), f"{language} page {start + offset + 1}", fill="black")
        sheet.save(images / f"sheet-{start // 12 + 1:02d}.png")
    print(language, "pages:", len(reader.pages), "all 6 contact destinations present on every page; bounds OK")
    print("Author metadata:", reader.metadata.author)
    print("Visual sheets:", images)


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    for language in ("english", "persian"):
        verify(language)
