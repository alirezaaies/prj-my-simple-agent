# Project status / وضعیت پروژه

Updated: **2026-10-14**, user timezone Asia/Tehran. Owner: **Alireza Khajehvandi / علیرضا خواجه‌وندی**.

## English

### Scope and decisions

The user requested completion of the personal free coding/research assistant, practical step-by-step teaching, a capability checklist, and adherence to `agent-guidelines/`. They selected the **terminal** interface. Their existing `.env` credential is authorized only for local tests; never print, record in docs/history, commit, or send its value as model input. The inference client necessarily uses it in the authentication header to Ollama cloud. No account purchase or paid plan change is authorized or needed.

The shared ChatGPT URL could not be retrieved after attempts; this implementation was based on the local source and all four guideline files. The original implementation was a 1064-line script plus a basic chat script. Neither loaded `.env`; the current local key variable name differed from the script's expected name. Missing/selected-interpreter dependencies, cwd-dependent JSON paths, corrupt-state resets, direct writes and unbounded context contributed to problems.

### Completed application

Continuous-task follow-up (2026-10-14): the user's transcript showed a successful HTML write followed by an empty model response and premature return to input. `Agent.ask` now continues empty/intermediate replies, uses a temporary `WorkPlan` with `plan_work`, `complete_step`, `finish_work` and `pause_work`, and verifies pending steps plus required file presence/size before finishing. File writes must belong to the plan, and equivalent relative paths are accepted. Declined actions stop subsequent batch actions; a completed plan also skips subsequent actions. `/plan` displays the latest checklist. Default budgets are 30 rounds plus a final limit summary and 8192 output tokens, configurable through public environment settings. Three stalled replies or three identical failed requests pause explicitly. File approvals, secret guards and network-error behavior remain enforced. The user's actual `myportfolio/` was not changed.

Follow-up language preference: **English is the default terminal and reply language** because Persian does not display well in the user's terminal. All built-in prompts/help are English. Model instructions default to English regardless of input language, with another language available only on explicit request. Documentation remains bilingual as originally requested.

- `run_agent.py` and `personal_agent/` provide maintained config, secret guard, JSON state, file/web tools, tool registry, model loop and CLI.
- `.env` is read relative to this repository. Both key names work; arbitrary remote API endpoints are rejected. Local endpoints use a dummy key even when a cloud key exists.
- Direct memory/task/file commands avoid model API usage. Natural-language actions use validated tool calls and explicit mutation review. One-shot mode denies model mutations.
- JSON state is copied once into ignored `data/`, retaining originals. Updates have validation, write locks, atomic replacement and previous valid backups. Task IDs remain monotonic. Corrupt files are not silently overwritten.
- Public HTTPS research validates redirects, rejects non-public IPs and pins the validated address for TLS. File operations are limited to supported small text/code files inside the workspace with secret/hidden/state-path exclusions.
- 30 tool rounds by default plus a final limit summary, six executions per round, explicit work-plan completion, and bounded complete-turn history. API failures avoid raw headers/body output. Successful tool effects are retained if a later model response fails.
- The former root scripts are compatibility launchers. Originals remain in `examples/legacy/`. User root JSON and `.env` were preserved.

### Validation evidence

- Continuous-task update: **51 tests, 50 passed, 1 Windows symlink test skipped**; `pip check` and whitespace checks passed. Regression tests reproduce HTML → empty reply → CSS/JS completion from one request, reject premature finish/missing files, recover truncated output, stop cancellation/stalls, validate limits, accept path aliases and skip actions after completion.
- Live `scripts/smoke_test.py --live --portfolio` passed from one prompt in a temporary workspace: all three files exist, HTML CSS/JS references match, the model read HTML back, and `finish_work` succeeded. The test did not change or send the user's actual portfolio/state. This does not verify browser behavior or universal semantic correctness.

- English-default follow-up: existing suite still **37 passed, 1 skipped**. Interactive startup/help, argument help, no-memory help and the confirmation prompt were checked in English. Isolated live Ollama checks passed for English output from a Persian input and Persian output on explicit request. Both reports were rebuilt and their changed pages visually checked; all-page contact/bounds checks passed (English 57 pages, Persian 55 pages).

- Python 3.12.13 on Windows; isolated `.venv`; `pip check` passed.
- 38 deterministic tests: **37 passed, 1 skipped**. Real symlink creation unavailable on this account; mocked resolved-path rejection also tested.
- Live `scripts/smoke_test.py --live`: cloud chat, task-tool roundtrip and reading/fixing a synthetic code file **passed**. Only temporary synthetic state/workspace was used.
- Live free web search and public Python tutorial retrieval **passed** and returned evidence URLs.
- `--check`, compatibility launchers, CLI commands and Git ignore checks inspected. No actual key values were shown.
- Final reports after the continuous-task update: **English 68 pages, Persian 65 pages**, both compiled with XeLaTeX → BibTeX → XeLaTeX twice. No overfull text, missing glyphs, unresolved references or footer-size warnings remained. All pages were rendered and visually reviewed; author/link/bounds checks passed again and the known credential was absent from maintained source and extracted PDF text.
- All pages were rendered with Poppler and reviewed in contact sheets; Persian body/reference pages were also inspected at larger resolution. All six exact contact destinations are PDF annotations on every page. Author metadata matches the report language; bounds and nonblank-page checks passed. Latin bibliography entries have explicit LTR direction; Persian headings/footers retain RTL direction.
- Known production credential scan found **zero occurrences** in public text files and extracted PDF text. Legacy root facts/tasks equal their migrated records; `.env` and root private files remain unchanged. Git ignore checks and `git diff --check` passed.

### Documentation and handoff rules

The root README is English first, then Persian. Practical tutorials and parallel reports live under `docs/english/` and `docs/persian/`; both include matching seven chapters, complete maintained source appendix, IEEE numbered `.bib` references, and exact author/contact information. Persian uses `xepersian` with 1.5 spacing. Font binaries, rendered previews, PDFs, temporary files and private state are ignored by Git. The six original contact destinations are centralized in each report config and must appear on every page.

Read `docs/report-guidelines/README.md` and all original `agent-guidelines/` files before extending documentation. `scripts/build_reports.py` recompiles without rewriting edited report sources. `scripts/prepare_reports.py --regenerate` deliberately replaces the LaTeX sources from the Markdown guides; do not run it over custom edits unintentionally. Rebuild reports after source changes because their appendix includes repository files directly. No sub-agents were used.

### Limits and optional next work

The first terminal application is functionally complete for the agreed scope. Not included: autonomous shell/test execution, GUI, PDF/image/audio ingestion, login/browser automation, background reminders, multi-user hosting, vector search, or unlimited free cloud. Local inference is configurable but was not run. Secret filtering covers known values and common patterns, not every unknown/encoded credential. Prompt guidance is not a formal guarantee of correct citations or injection immunity. Backups can retain deleted facts. DNS resolver calls can exceed a practical network budget.

Optional future work, after real use: gather redacted examples of model mistakes; introduce structured patches for larger files; choose a graphical interface only if requested; improve research evaluation against a curated primary-source set. None of those is a hidden unfinished requirement of this first terminal release. No commit, push, publication or deployment was performed.

## فارسی

طبق درخواست بعدی کاربر، رابط ترمینال و پاسخ‌های پیش‌فرض مدل انگلیسی شدند، حتی اگر ورودی فارسی باشد. پاسخ فارسی یا زبان دیگر فقط با درخواست صریح کاربر ارائه می‌شود. مستندات همچنان دوزبانه هستند.

کاربر نسخهٔ ترمینالی ساده را انتخاب کرد. هستهٔ قابل استفاده کامل شده: گفتگو، حافظهٔ صریح، کارهای شخصی، تحقیق عمومی وب، خواندن کد و تغییر فایل کوچک با نمایش تفاوت و تأیید. نام فعلی کلید در `.env` بدون تغییر پشتیبانی می‌شود؛ کلید فقط در احراز هویت Ollama استفاده شده و در متن گفتگو یا گزارش ثبت نشده است.

کد قدیمی برای حفظ آموزش در `examples/legacy/` نگه داشته شد؛ فایل‌های ریشه نسخهٔ جدید را اجرا می‌کنند. حافظه و کارهای قبلی حفظ و یک‌بار به `data/` کپی شدند. دادهٔ خراب خودکار خالی یا جایگزین نمی‌شود. پوشهٔ داده و کلید و پشتیبان وارد Git نمی‌شوند.

شواهد فعلی کد: ۵۱ آزمون محلی، ۵۰ پاس و یک تست symlink بدون مجوز ویندوز اجرا نشده است. تست تازه، پاسخ خالی پس از HTML را بازسازی می‌کند و CSS و JS را بدون درخواست دوم می‌سازد. تست واقعی سه فایل و تطابق ارجاع و پایان برنامه با یک درخواست در پوشهٔ موقت پاس شد. پورتفولیوی واقعی کاربر و دادهٔ شخصی تغییر نکردند. وجود فایل و پایان برنامه تضمین اجرای مرورگر و درستی عمومی کد نیست.

ادامهٔ خودکار اکنون برنامهٔ موقت WorkPlan دارد و با /plan دیده می‌شود. مدل پس از پاسخ خالی یا میانی خودکار ادامه می‌دهد، ولی لغو تغییر، خطای شبکه، سه پاسخ بی‌پیشرفت یا سه خطای یکسان توقف صریح می‌دهد. سقف پیش‌فرض ۳۰ دور و ۸۱۹۲ توکن خروجی است و از تنظیم عمومی محیط قابل تغییر است. تأیید فایل و محافظت کلید برقرارند.

گزارش دوزبانه در `docs/`، ساختار فصل‌ها متناظر، کد کامل در ضمیمه و نام و شش لینک نویسنده در قالب ثبت شده‌اند. برای ادامه، اول همین فایل، سپس قواعد گزارش و چهار راهنمای اصلی را بخوانید. ساخت گزارش با `build_reports.py` و بازتولید جایگزین‌کنندهٔ منبع با `prepare_reports.py --regenerate` دو کار جدا هستند.

نتایج نهایی PDF پس از اصلاح ادامهٔ خودکار: گزارش فارسی ۶۵ صفحه و انگلیسی ۶۸ صفحه؛ هر دو با منبع قابل ویرایش و ضمیمهٔ کد تازه ساخته شدند. خطای فونت و بیرون‌زدگی و مرجع حل‌نشده باقی نماند. تصویر همهٔ صفحات مرور شد، مقصد دقیق هر شش لینک در همهٔ صفحات و نام نویسنده در فراداده بررسی شد. جهت منابع لاتین در فارسی درست است. کلید واقعی در منبع نگهداری‌شده و متن استخراج‌شدهٔ PDF یافت نشد؛ پورتفولیو و دادهٔ شخصی کاربر دست‌نخورده‌اند.

انتشار و commit انجام نشده است. رابط گرافیکی و اجرای خودکار کد و مرورگر و PDFخوانی و یادآوری پس‌زمینه جزو نسخهٔ توافق‌شده نیستند. رایگان بودن کتابخانه با cloud رایگان نامحدود یکسان نیست. توسعهٔ بعدی اختیاری بهتر است از یک مشکل مشخص کار روزمره شروع شود.
