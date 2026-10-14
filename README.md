# My Personal Agent

Author and project owner: **Alireza Khajehvandi / علیرضا خواجه‌وندی**

[Portfolio](https://alirezaaies.github.io/) · [GitHub](https://github.com/alirezaaies) · [LinkedIn](https://www.linkedin.com/in/alirezakhajehvandi) · [YouTube](https://www.youtube.com/@AlirezaAIES) · [Telegram](https://t.me/AlirezaAIES) · [Instagram](https://www.instagram.com/alireza.aies)

## English

A small terminal assistant for learning, coding and source-based research. It connects to Ollama cloud or a local Ollama server, manages explicit saved facts and tasks, searches public webpages, and proposes project file changes with a reviewable diff.

### Start on Windows

The terminal interface and agent replies default to **English**, even when a request is written in another language. To receive Persian or another language, explicitly ask for it, for example: "Explain this in Persian."

Python 3.11 or newer is required; this version was tested with Python 3.12.13.
Open a PowerShell terminal in this project folder:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
# Only on a fresh checkout WITHOUT .env:
Copy-Item .env.example .env
# Edit .env locally; never paste its contents into a chat or issue.
.\.venv\Scripts\python.exe run_agent.py --check
.\.venv\Scripts\python.exe run_agent.py
```

**Your existing `.env` already works. Do not replace it.** Both `OLLAMA_API_KEY` and the earlier `OLLAMA_FREE_API_KEY` name are accepted. Defaults: `https://ollama.com/v1`, model `gemma4:31b`. The API key is used for authentication only. No key values appear in `/status`.

### Try these commands

```text
/help
/status
/remember I prefer step-by-step Python explanations
/memory
/update I prefer step-by-step Python explanations | I prefer short Python examples
/task Practice Python functions
/tasks
/done 1
/files
/read README.md
/search Python official tutorial
/open https://docs.python.org/3/tutorial/
/reset
/exit
```

Use the ID actually shown by `/tasks`; the example `1` is not guaranteed to exist. `/forget TEXT`, `/forget-all` and `/delete-task ID` require `YES` before deletion. Direct memory/task/file commands do not call the model. Web commands need internet, but do not call Ollama.

Ask naturally: “Read demo.py, explain the bug, and propose a minimal fix.” Model-requested state changes and file writes show a preview and require `YES`. Enter cancels. Review saved changes with `git diff` and run your own project tests. The assistant has no shell execution tool and cannot claim it ran code.

```powershell
# Work on a different code folder:
.\.venv\Scripts\python.exe run_agent.py --workspace 'E:\path\to\your-project'
# Stateless chat (no saved memory/task tools):
.\.venv\Scripts\python.exe run_agent.py --no-memory
# One-shot; proposed mutations are automatically denied:
.\.venv\Scripts\python.exe run_agent.py --ask 'Explain Python list comprehensions'
# Offline regression suite; no API usage:
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
# Optional real API integration test, using temporary synthetic data:
.\.venv\Scripts\python.exe scripts\smoke_test.py --live
```

### Free/local operation and privacy

The code uses free libraries. Ollama cloud has account/model availability and usage-credit limits; “free” does not mean unlimited cloud use. Check the current [Ollama pricing](https://ollama.com/pricing). To avoid cloud API usage, install Ollama separately, download a model your hardware can run, then set these **non-secret** settings in your local `.env`:

```text
OLLAMA_BASE_URL=http://localhost:11434/v1
OLLAMA_MODEL=qwen3:8b
```

For example, run `ollama pull qwen3:8b` and keep the local server running. Local model performance/tool reliability depends on hardware and model. Local inference was **not** tested on this machine. Your cloud key is not sent to the local server.

Cloud mode sends chat, saved preferences, and selected file excerpts to Ollama. Search queries go to search providers. `.env`, hidden paths, state files and common credential paths are blocked from file tools; known credentials are redacted/rejected. These checks do not identify every possible secret: only share code suitable for the selected service. History is kept in process memory for up to ten complete recent turns; it is not saved as a chat transcript.

State lives in ignored `data/memory.json` and `data/tasks.json`. The old root JSON files are copied on first launch and preserved. Valid prior states get `.json.bak` backups. Corrupt state causes an error rather than silent data loss. See the [tutorial](docs/persian/guide.md) and [troubleshooting](docs/english/guide.md).

### Continuous tasks

Give a multi-step request once. Before writing files, the agent records a temporary checklist and all required output paths, then keeps working through them. Empty or intermediate replies trigger automatic continuation; a complete checklist plus non-empty required files is needed before `finish_work` returns the final summary. `/plan` shows the most recent checklist. This checks artifact presence, not execution or correctness of the code.

For example: "Create myportfolio/index.html, myportfolio/style.css and myportfolio/script.js. Finish all three and review the HTML references." Approve each proposed write with `YES`; you do not need to send a separate "continue" prompt after a file is saved. Declining a change stops the task and preserves earlier approved changes. Ctrl+C interrupts the run.

Defaults are 30 tool rounds plus a final limit summary, and an output cap of 8192 tokens per model response. Three replies without tool progress or three identical failed tool requests pause the run. Connection/usage errors also stop honestly. Optional public settings in `.env` are `AGENT_MAX_ROUNDS` (1-100) and `AGENT_MAX_OUTPUT_TOKENS` (256-32768). No API-key change is needed. `--ask` still denies model-proposed changes, so use interactive mode for file creation.

To reproduce the live three-file test in an isolated temporary directory:

```powershell
.\.venv\Scripts\python.exe scripts\smoke_test.py --live --portfolio
```

### Structure and evidence

| Location | Purpose |
| --- | --- |
| `run_agent.py`, `personal_agent/` | Current application, separated into config, storage, tools, files, web, chat and CLI |
| `assistant_withmemory.py`, `assistant_withoutmemory.py` | Compatible launchers for earlier filenames |
| `examples/legacy/` | Preserved original learning scripts; not recommended entry points |
| `tests/` | Deterministic tests with fake data and a fake model |
| `scripts/smoke_test.py` | Explicit opt-in live cloud check |
| `docs/english/`, `docs/persian/` | Tutorials and editable LaTeX/PDF reports |
| `PROJECT_STATUS.md` | Handoff state, evidence, limits, and future work |

Validated on 2026-10-14: 51 offline tests (50 passed, 1 Windows symlink test skipped); live cloud chat, task tool roundtrip and approved code edit passed; live public-page read and web search passed. The live continuous portfolio test created all three files, validated the CSS/JS references and passed the completion check from one prompt. This is evidence for the tested scenarios, not a guarantee that all model responses are correct. The shared ChatGPT history could not be retrieved; the audit used the local source and guidelines.

## فارسی

این پروژه دستیار شخصی من برای یادگیری، کدنویسی و تحقیق در ترمینال است. مدل می‌تواند ابزار بخواهد، اما اعتبارسنجی و اجرای ابزار را کد Python انجام می‌دهد. حافظه و کارها روی سیستم ذخیره می‌شوند؛ تغییر پیشنهادی مدل قبل از ذخیره به شما نشان داده می‌شود.

### شروع سریع

زبان پیش‌فرض رابط ترمینال و پاسخ مدل **انگلیسی** است، حتی اگر درخواست فارسی باشد. برای پاسخ فارسی یا زبان دیگر، صریحاً آن زبان را درخواست کنید؛ مثلاً بنویسید: «این موضوع را به فارسی توضیح بده».

در PowerShell داخل پوشهٔ پروژه، این دو دستور را اجرا کنید. محیط `.venv` و وابستگی‌ها در این سیستم آماده شده‌اند:

```powershell
.\.venv\Scripts\python.exe run_agent.py --check
.\.venv\Scripts\python.exe run_agent.py
```

برای نصب از صفر، ابتدا `python -m venv .venv` و سپس `.\.venv\Scripts\python.exe -m pip install -r requirements.txt` را اجرا کنید. فقط اگر `.env` ندارید، فایل `.env.example` را به `.env` کپی کنید و کلید را داخل همان فایل محلی وارد کنید. **فایل فعلی `.env` شما نیاز به جایگزینی ندارد.** نام قدیمی `OLLAMA_FREE_API_KEY` نیز پشتیبانی می‌شود.

### تمرین ده‌دقیقه‌ای

1. `/help` را بزنید تا دستورها را ببینید؛ `/status` تنظیمات عمومی را نشان می‌دهد.
2. `/remember توضیح مرحله‌به‌مرحله پایتون را ترجیح می‌دهم` را بنویسید و با `/memory` ذخیره را بررسی کنید.
3. با `/task تمرین تابع‌های پایتون` یک کار بسازید؛ `/tasks` شناسه را نشان می‌دهد. `/done ID` آن را تکمیل می‌کند؛ به‌جای `ID` عدد واقعی را بنویسید.
4. `/files` و `/read README.md` را امتحان کنید. برای پروژهٔ دیگر از `--workspace` استفاده کنید.
5. برای تحقیق، `/search Python official tutorial` و سپس `/open https://docs.python.org/3/tutorial/` را امتحان کنید.
6. برای کمک هوشمند بنویسید: «فایل demo.py را بخوان، علت خطا را توضیح بده و اصلاح کوچک پیشنهاد کن». مسیر و تفاوت فایل را بررسی کنید؛ فقط اگر تغییر درست است `YES` بنویسید. Enter تغییر را لغو می‌کند.
7. `/reset` فقط تاریخچهٔ گفتگو را پاک می‌کند؛ `/exit` برنامه را می‌بندد.

دستورهای مستقیم حافظه و کارها مصرف API ندارند. گفتگو و انتخاب ابزار توسط مدل مصرف اعتبار Ollama دارد. نتایج تحقیق باید با URL واقعی همراه باشند؛ وجود لینک به‌تنهایی درستی ادعا را ثابت نمی‌کند. این نسخه اجرای خودکار کد، PDFخوانی، مرور صفحات نیازمند ورود یا کنترل مرورگر ندارد.

### حریم خصوصی، هزینه و خطاها

برای کار چندمرحله‌ای فقط یک‌بار درخواست بدهید. ایجنت پیش از نوشتن فایل، برنامهٔ موقت و همهٔ مسیرهای خروجی را ثبت می‌کند و پس از پاسخ خالی یا میانی خودکار ادامه می‌دهد. برای پایان، همهٔ گام‌ها و وجود فایل‌های غیرخالی بررسی می‌شوند؛ این بررسی به معنی اجرای کد یا تضمین درستی آن نیست. با `/plan` آخرین برنامه را می‌بینید. همچنان هر ذخیره با `YES` تأیید می‌شود؛ لازم نیست پس از فایل اول درخواست «ادامه بده» بفرستید.

پیش‌فرض ۳۰ دور ابزار و سقف خروجی ۸۱۹۲ توکن است. پس از لغو تغییر، خطای اتصال، سه پاسخ بی‌پیشرفت یا سه خطای یکسان، توقف صریح گزارش می‌شود و تغییر قبلی حفظ می‌شود. تنظیم عمومی `AGENT_MAX_ROUNDS` و `AGENT_MAX_OUTPUT_TOKENS` اختیاری است؛ کلید API نیاز به تغییر ندارد. تست واقعی سه فایل پورتفولیو با یک درخواست در پوشهٔ موقت موفق بود.

کلید داخل `.env` باقی می‌ماند، وارد گزارش و Git نمی‌شود و فقط برای احراز هویت اتصال cloud استفاده می‌شود. در حالت cloud، گفتگو، نکته‌های حافظه و بخش انتخاب‌شده از فایل برای Ollama ارسال می‌شوند. متن سرچ نیز به سرویس‌های جستجو می‌رود. کلیدهای شناخته‌شده و قالب‌های رایج اطلاعات محرمانه مسدود یا پوشانده می‌شوند؛ تشخیص همهٔ انواع راز ممکن نیست.

کتابخانه‌ها رایگان‌اند، اما [اعتبار رایگان Ollama cloud محدود است](https://ollama.com/pricing). برای اجرای محلی، Ollama را نصب کنید، مثلاً `ollama pull qwen3:8b` را اجرا کنید، و دو تنظیم بالا را در `.env` بگذارید. اجرای مدل محلی به توان سخت‌افزار بستگی دارد و در این سیستم تست نشده است.

اگر پیام خطا دیدید، بخش رفع اشکال [راهنمای فارسی](docs/persian/guide.md) را بخوانید. دادهٔ خراب خودکار پاک نمی‌شود. برای بازیابی، پس از بستن برنامه از نسخهٔ پشتیبان داخل `data/` استفاده کنید. فایل‌های قدیمی حافظه و کارها دست‌نخورده نگه داشته شده‌اند؛ نسخهٔ فعال در `data/` است.

راهنمای آموزشی کامل، گزارش قابل ویرایش و PDF در [پوشهٔ مستندات](docs/README.md) قرار دارند. [چک‌لیست قابلیت‌ها](docs/CAPABILITIES.md) مشخص می‌کند چه چیزی پیاده‌سازی و چه چیزی واقعاً تست شده است. مالک و مدیر پروژه: **علیرضا خواجه‌وندی**.
