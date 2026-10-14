"""Build editable bilingual reports with XeLaTeX and BibTeX."""
import argparse
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
FONTS = {
    "Vazirmatn-Regular.ttf": "https://raw.githubusercontent.com/rastikerdar/vazirmatn/master/fonts/ttf/Vazirmatn-Regular.ttf",
    "Vazirmatn-Bold.ttf": "https://raw.githubusercontent.com/rastikerdar/vazirmatn/master/fonts/ttf/Vazirmatn-Bold.ttf",
    "NotoSans-Regular.ttf": "https://raw.githubusercontent.com/notofonts/noto-fonts/main/hinted/ttf/NotoSans/NotoSans-Regular.ttf",
    "NotoSans-Bold.ttf": "https://raw.githubusercontent.com/notofonts/noto-fonts/main/hinted/ttf/NotoSans/NotoSans-Bold.ttf",
    "DejaVuSansMono.ttf": "https://raw.githubusercontent.com/matplotlib/matplotlib/main/lib/matplotlib/mpl-data/fonts/ttf/DejaVuSansMono.ttf",
}


def download_fonts():
    import requests
    folder = ROOT / "docs/fonts"
    folder.mkdir(parents=True, exist_ok=True)
    for name, url in FONTS.items():
        path = folder / name
        if path.exists():
            continue
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        if not response.content.startswith((b"\x00\x01\x00\x00", b"OTTO")):
            raise ValueError("Downloaded font has invalid format: " + name)
        path.write_bytes(response.content)
        print("Downloaded free font:", name)


def build(language):
    folder = ROOT / "docs" / language
    commands = [["xelatex", "-interaction=nonstopmode", "-halt-on-error", "main_report.tex"],
                ["bibtex", "main_report"],
                ["xelatex", "-interaction=nonstopmode", "-halt-on-error", "main_report.tex"],
                ["xelatex", "-interaction=nonstopmode", "-halt-on-error", "main_report.tex"]]
    for command in commands:
        process = subprocess.run(command, cwd=folder, text=True, encoding="utf-8", errors="replace",
                                 stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=180)
        if process.returncode:
            print(process.stdout[-8000:])
            raise RuntimeError(f"{language}: {command[0]} failed; inspect main_report.log")
    log = (folder / "main_report.log").read_text(encoding="utf-8", errors="replace")
    warnings = [line for line in log.splitlines() if any(s in line for s in (
        "Overfull", "Missing character", "undefined", "too small"))]
    if warnings:
        print("Layout/reference warnings:", language)
        print("\n".join(dict.fromkeys(warnings)))
        raise RuntimeError("Resolve report warnings before delivery.")
    print("Built:", folder / "main_report.pdf")


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser()
    parser.add_argument("--download-fonts", action="store_true")
    args = parser.parse_args()
    if args.download_fonts:
        download_fonts()
    for executable in ("xelatex", "bibtex"):
        if not shutil.which(executable):
            raise RuntimeError("Missing report dependency: " + executable)
    for language in ("english", "persian"):
        build(language)


if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        print("Report build failed:", type(error).__name__, str(error))
        sys.exit(1)
