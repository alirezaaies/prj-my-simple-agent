# Documentation / مستندات

Author: **Alireza Khajehvandi / علیرضا خواجه‌وندی**.

## English

Read `english/guide.md` for the practical tutorial and `CAPABILITIES.md` for the tested checklist. Editable reports use matching layouts in `english/` and `persian/`: `main_report.tex`, `config.tex`, `formatter.tex`, `chapters/`, `references.bib`. PDFs are generated locally and ignored by Git. Full current application source is included from repository files in the report appendix; rebuilding updates it automatically. No `.env`, personal JSON state, or API key is included.

Build both reports from the project root:

```powershell
.\.venv\Scripts\python.exe scripts\build_reports.py
```

Requires XeLaTeX and BibTeX (MiKTeX or TeX Live) plus the LaTeX packages listed in `config.tex`. Persian uses `xepersian`; font preference is local `docs/fonts/Vazirmatn-Regular.ttf`, installed Vazirmatn, IRANSansX, IRANSans, then B Nazanin. English prefers local Noto Sans, then installed FreeSans/Noto Sans/DejaVu Sans, then TeX Gyre Heros. Fonts and generated preview images remain local. Font sources and licensing are in `fonts/README.md`; the build script can download free fonts using `--download-fonts`.

In TeXstudio, open the relevant `main_report.tex`, choose XeLaTeX, and run XeLaTeX → BibTeX → XeLaTeX → XeLaTeX. The report needs the relative project source paths for its appendix. Compile from its language directory. Rebuild after application changes and review page renders before delivery. Continuation rules are in `report-guidelines/README.md`; project state is in `../PROJECT_STATUS.md`.

Optional automated checks and page renders:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements-docs.txt
.\.venv\Scripts\python.exe scripts\verify_reports.py
```

The verifier checks six contact destinations on every page, author metadata, nonblank pages and text bounds, then renders contact sheets using Poppler. Inspect those images visually; automated bounds checks do not establish reading order. `scripts/prepare_reports.py --regenerate` replaces report sources from the Markdown tutorials, including any manual TeX edits; use it only intentionally.

## فارسی

برای یادگیری و استفاده، ابتدا `persian/guide.md` را بخوانید. چک‌لیست واقعی قابلیت‌ها در `CAPABILITIES.md` است. گزارش فارسی و انگلیسی ساختار و رنگ‌بندی یکسان دارند و هر فصل در فایل جداگانه قرار گرفته است. منبع کامل کد فعلی از خود فایل‌های پروژه در ضمیمه خوانده می‌شود؛ پس پس از تغییر کد، گزارش را دوباره بسازید. `.env` و حافظه و کارهای شخصی وارد گزارش نمی‌شوند.

دستور ساخت بالا از ریشهٔ پروژه، هر دو PDF را می‌سازد. در TeXstudio هم می‌توانید `main_report.tex` هر زبان را باز کنید و موتور XeLaTeX را انتخاب کنید. ترتیب ساخت: XeLaTeX، سپس BibTeX، سپس دو بار XeLaTeX. کامپایل باید از پوشهٔ همان زبان باشد تا مسیرهای نسبی ضمیمه درست خوانده شوند.

فونت، PDF، فایل‌های کمکی و تصاویر بررسی خروجی داخل Git نمی‌روند. تنظیم فونت و رنگ و نام نویسنده در `config.tex` و تنظیم جلد در `formatter.tex` است. راهنمای ادامهٔ گزارش در `report-guidelines/README.md` و وضعیت تحویل در `PROJECT_STATUS.md` ثبت شده است.
