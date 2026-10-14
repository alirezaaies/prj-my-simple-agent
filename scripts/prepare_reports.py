"""Regenerate LaTeX from guides; explicit opt-in because it replaces edited report sources."""
import argparse
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
LINKS = [
    ("Portfolio", "وب‌سایت", "https://alirezaaies.github.io/"),
    ("GitHub", "گیت‌هاب", "https://github.com/alirezaaies"),
    ("LinkedIn", "لینکدین", "https://www.linkedin.com/in/alirezakhajehvandi"),
    ("YouTube", "یوتیوب", "https://www.youtube.com/@AlirezaAIES"),
    ("Telegram", "تلگرام", "https://t.me/AlirezaAIES"),
    ("Instagram", "اینستاگرام", "https://www.instagram.com/alireza.aies"),
]


def escape(text):
    replacements = {"\\": r"\textbackslash{}", "&": r"\&", "%": r"\%", "$": r"\$",
                    "#": r"\#", "_": r"\_", "{": r"\{", "}": r"\}", "~": r"\textasciitilde{}",
                    "^": r"\textasciicircum{}", "→": r"\(\rightarrow\)"}
    return "".join(replacements.get(c, c) for c in text)


def paragraph(text, persian):
    if not persian:
        return escape(text)
    # Keep Latin fragments on independent source lines, per the report guidelines.
    parts = re.split(r"([A-Za-z][A-Za-z0-9_./:-]*(?: [A-Za-z0-9][A-Za-z0-9_./:-]*)*)", text)
    return "\n".join(r"\lr{" + escape(part) + "}" if i % 2 else escape(part)
                     for i, part in enumerate(parts) if part)


def chapter(body, persian):
    result, block = [], False
    for line in body.splitlines():
        if line.startswith("```"):
            if not block:
                if persian:
                    result.append(r"\begin{LTR}")
                result.append(r"\begin{Verbatim}[breaklines,breakanywhere,fontsize=\small]")
            else:
                result.append(r"\end{Verbatim}")
                if persian:
                    result.append(r"\end{LTR}")
            block = not block
        elif block:
            result.append(line)
        else:
            result.append(paragraph(line, persian))
    return "\n".join(result) + "\n"


BASE_CONFIG = r"""\usepackage[a4paper,left=23mm,right=23mm,top=22mm,bottom=20mm,includeheadfoot,headheight=15pt,footskip=58pt]{geometry}
\usepackage{fontspec}
\usepackage{xcolor}
\definecolor{accent}{HTML}{176B78}
\usepackage{setspace}
\usepackage{fvextra}
\usepackage{fancyhdr}
\usepackage{titlesec}
\usepackage{xurl}
\usepackage[unicode,colorlinks=true,linkcolor=accent,urlcolor=accent,citecolor=accent]{hyperref}
\IfFileExists{../fonts/DejaVuSansMono.ttf}{
  \setmonofont{DejaVuSansMono.ttf}[Path=../fonts/]
}{\setmonofont{Courier New}}
\setlength{\parindent}{0pt}
\setlength{\parskip}{6pt}
\emergencystretch=3em
\DefineVerbatimEnvironment{Verbatim}{Verbatim}{breaklines,breakanywhere,fontsize=\small}
\fvset{codes={\catcode"200C=9\catcode"200F=9}}
"""


def config(persian):
    text = BASE_CONFIG
    if persian:
        text += r"""\usepackage{xepersian}
\IfFileExists{../fonts/Vazirmatn-Regular.ttf}{
  \settextfont{Vazirmatn-Regular.ttf}[Path=../fonts/,BoldFont=Vazirmatn-Bold.ttf]
}{\IfFontExistsTF{Vazirmatn}{\settextfont{Vazirmatn}}{
  \IfFontExistsTF{IRANSansX}{\settextfont{IRANSansX}}{
    \IfFontExistsTF{IRANSans}{\settextfont{IRANSans}}{\settextfont{B Nazanin}}}}}
\IfFileExists{../fonts/NotoSans-Regular.ttf}{
  \setlatintextfont{NotoSans-Regular.ttf}[Path=../fonts/,BoldFont=NotoSans-Bold.ttf]
}{\setlatintextfont{TeX Gyre Heros}}
\onehalfspacing
\setLTRbibitems
% bidi inserts an invisible RLM near digits. Use a text font that contains it,
% including inside monospaced code; preserve direction without missing glyphs.
\makeatletter
\renewcommand*{\DigitsDotDashInterCharToks}{\if@nonlatin{\normalfont\char"200F }\fi}
\makeatother
\newcommand{\AuthorName}{علیرضا خواجه‌وندی}
\newcommand{\ReportTitle}{ایجنت شخصی برای کدنویسی و تحقیق}
\newcommand{\ContactHeading}{صفحات مجازی علیرضا خواجه‌وندی}
\newcommand{\PageLabel}{صفحهٔ}
"""
    else:
        text += r"""\IfFileExists{../fonts/NotoSans-Regular.ttf}{
  \setmainfont{NotoSans-Regular.ttf}[Path=../fonts/,BoldFont=NotoSans-Bold.ttf]
}{\IfFontExistsTF{FreeSans}{\setmainfont{FreeSans}}{
  \IfFontExistsTF{Noto Sans}{\setmainfont{Noto Sans}}{
    \IfFontExistsTF{DejaVu Sans}{\setmainfont{DejaVu Sans}}{\setmainfont{TeX Gyre Heros}}}}}
\setstretch{1.25}
\newcommand{\AuthorName}{Alireza Khajehvandi}
\newcommand{\ReportTitle}{Personal Agent for Coding and Research}
\newcommand{\ContactHeading}{Alireza Khajehvandi online}
\newcommand{\PageLabel}{Page}
"""
    # Apply heading styles after xepersian/bidi has installed its chapter hooks.
    text += r"""\titleformat{\chapter}[display]{\color{accent}\Large\bfseries}{\thechapter}{4pt}{\Huge}
\titlespacing*{\chapter}{0pt}{0pt}{16pt}
\titleformat{\section}{\color{accent}\large\bfseries}{\thesection}{0.5em}{}
"""
    for i, (en, fa, url) in enumerate(LINKS):
        text += r"\newcommand{\Contact" + chr(65 + i) + "}{\\href{" + url + "}{" + (fa if persian else en) + "}}\n"
    text += r"""\newcommand{\ContactRows}{
\ContactA\quad\ContactB\quad\ContactC\\
\ContactD\quad\ContactE\quad\ContactF}
\newcommand{\ReportFooter}{\parbox{\textwidth}{\centering\fontsize{9}{11}\selectfont
\ContactHeading\\\ContactRows\\\PageLabel\ \thepage}}
\pagestyle{fancy}
\fancyhf{}
\fancyhead[C]{\fontsize{8}{10}\selectfont\ReportTitle\quad|\quad\AuthorName}
\fancyfoot[C]{\ReportFooter}
\renewcommand{\headrulewidth}{0.3pt}
\renewcommand{\footrulewidth}{0.3pt}
\fancypagestyle{plain}{\fancyhf{}\fancyfoot[C]{\ReportFooter}\renewcommand{\headrulewidth}{0pt}}
\hypersetup{pdftitle={\ReportTitle},pdfauthor={\AuthorName}}
"""
    return text


def prepare(language):
    persian = language == "persian"
    folder = ROOT / "docs" / language
    chapters = folder / "chapters"
    chapters.mkdir(parents=True, exist_ok=True)
    (folder / "config.tex").write_text(config(persian), encoding="utf-8")
    sub = "آموزش عملی، معماری، آزمون و کد کامل" if persian else "Practical tutorial, architecture, verification and complete source"
    author = "نویسنده:" if persian else "Author:"
    date = "نسخهٔ بررسی‌شده: ۲۰۲۶-۱۰-۱۴" if persian else "Checked version: 2026-10-14"
    formatter = r"""\begin{titlepage}
\thispagestyle{plain}
\centering
\vspace*{18mm}
{\color{accent}\Huge\bfseries\ReportTitle\par}
\vspace{8mm}
{\Large """ + sub + r"""\par}
\vspace{18mm}
{\Large """ + author + r" \AuthorName\par}" + "\n" + r"""\vfill
{\large """ + date + r"""\par}
\vspace{10mm}
{\ContactHeading\par}
\medskip
\ContactRows
\vspace{14mm}
\end{titlepage}
"""
    (folder / "formatter.tex").write_text(formatter, encoding="utf-8")
    guide = (folder / "guide.md").read_text(encoding="utf-8")
    sections = re.split(r"^## ", guide, flags=re.MULTILINE)[1:]
    files = []
    topics = ["scope", "setup", "usage", "coding_research", "implementation", "verification", "capabilities"]
    for i, section in enumerate(sections):
        heading, body = section.split("\n", 1)
        heading = re.sub(r"^[0-9۰-۹]+[.،\s]+", "", heading)
        name = f"{i+1:02d}_{topics[i]}.tex"
        files.append(name)
        content = r"\chapter{" + paragraph(heading, persian) + "}\n" + chapter(body, persian)
        if i == 1:
            content += ("\\cite{ollama-api,ollama-pricing}\n")
        if i == 3:
            content += "\\cite{ddgs}\n"
        if i == 5:
            content += "\\cite{python-unittest}\n"
        (chapters / name).write_text(content, encoding="utf-8")
    title = "منبع کامل برنامه و آزمون‌ها" if persian else "Complete application and test source"
    appendix = r"\chapter{" + title + "}\n"
    source_paths = ["run_agent.py", "assistant_withmemory.py", "assistant_withoutmemory.py"]
    source_paths += [p.relative_to(ROOT).as_posix() for p in sorted((ROOT / "personal_agent").glob("*.py"))]
    source_paths += ["tests/test_agent.py"]
    source_paths += [p.relative_to(ROOT).as_posix() for p in sorted((ROOT / "scripts").glob("*.py"))]
    for path in source_paths:
        appendix += "\\section{" + (r"\lr{" if persian else "") + escape(path) + ("}" if persian else "") + "}\n"
        if persian:
            appendix += "\\begin{LTR}\n"
        appendix += r"\VerbatimInput[breaklines,breakanywhere,fontsize=\footnotesize]{../../" + path + "}\n"
        if persian:
            appendix += "\\end{LTR}\n"
    (chapters / "08_source.tex").write_text(appendix, encoding="utf-8")
    final_title = "دربارهٔ نویسنده و راه‌های ارتباطی" if persian else "About the author and contact"
    contacts = r"\chapter*{" + final_title + "}\n\\addcontentsline{toc}{chapter}{" + final_title + "}\n\\AuthorName\n\n"
    for en, fa, url in LINKS:
        contacts += (fa if persian else en) + ":\n" + (r"\lr{" if persian else "") + r"\url{" + url + "}" + ("}" if persian else "") + "\n\n"
    (chapters / "09_contact.tex").write_text(contacts, encoding="utf-8")
    main = r"% !TeX program = xelatex" + "\n" + r"""\documentclass[11pt,a4paper,oneside]{report}
\input{config}
\begin{document}
\input{formatter}
\setcounter{page}{2}
\tableofcontents
"""
    main += "\n".join(r"\input{chapters/" + f[:-4] + "}" for f in files)
    main += "\n\\appendix\n\\input{chapters/08_source}\n\\bibliographystyle{IEEEtran}\n\\bibliography{references}\n\\input{chapters/09_contact}\n\\end{document}\n"
    (folder / "main_report.tex").write_text(main, encoding="utf-8")
    references = r"""@misc{ollama-api,
 author={{Ollama}}, title={OpenAI compatibility},
 howpublished={\url{https://docs.ollama.com/api/openai-compatibility}}, note={Accessed 2026-10-14}}
@misc{ollama-pricing,
 author={{Ollama}}, title={Pricing and usage limits},
 howpublished={\url{https://ollama.com/pricing}}, note={Accessed 2026-10-14}}
@misc{python-unittest,
 author={{Python Software Foundation}}, title={unittest: Unit testing framework},
 howpublished={\url{https://docs.python.org/3/library/unittest.html}}, note={Accessed 2026-10-14}}
@misc{ddgs,
 author={{DDGS contributors}}, title={DDGS metasearch library},
 howpublished={\url{https://github.com/deedy5/ddgs}}, note={Accessed 2026-10-14}}
"""
    (folder / "references.bib").write_text(references, encoding="utf-8")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--regenerate", action="store_true", required=True)
    parser.parse_args()
    for language in ("english", "persian"):
        prepare(language)
    print("Report sources regenerated. Build and visually verify both reports.")
