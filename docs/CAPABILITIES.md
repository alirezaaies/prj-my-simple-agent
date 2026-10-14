# Capability checklist / چک‌لیست قابلیت‌ها

Author: **Alireza Khajehvandi / علیرضا خواجه‌وندی**. Checked: 2026-10-14.

| Capability / قابلیت | How to use / روش استفاده | Evidence / شواهد |
| --- | --- | --- |
| [x] English-default conversation; other languages on request / گفتگو با پیش‌فرض انگلیسی | Write a normal request; explicitly ask for Persian when needed / برای پاسخ فارسی صریحاً درخواست کنید | Cloud smoke chat passed / تست واقعی پاس شد |
| [x] Coding explanation and suggestions / توضیح و پیشنهاد کد | Ask to inspect a named file / نام فایل را بدهید | Sample add-function fix passed / اصلاح فایل نمونه پاس شد |
| [x] List/read project text files / فهرست و خواندن فایل | `/files`, `/read PATH`, `--workspace` | Offline file/security tests passed |
| [x] Reviewed file writes / ذخیرهٔ تغییر با بررسی | Model proposes `write_file`; review diff, type `YES` | Synthetic live edit and cancellation tests passed |
| [x] Public web search / جستجوی وب | `/search QUERY` or ask for research | Live search returned URLs |
| [x] Public HTML reading / خواندن HTML عمومی | `/open HTTPS_URL` | Live Python tutorial retrieval passed |
| [x] Explicit saved facts / حافظهٔ صریح | `/remember TEXT`, `/memory` | Offline CRUD/duplicate tests passed |
| [x] Correct/delete facts / اصلاح و حذف حافظه | `/update OLD | NEW`, `/forget TEXT`, `/forget-all` | Offline update/cancel tests; deletion approval required |
| [x] Personal tasks / کارهای شخصی | `/task TITLE`, `/tasks`, `/done ID`, `/delete-task ID` | Offline lifecycle plus live create-task roundtrip |
| [x] Context reset / پاک کردن گفتگو | `/reset` | Clears in-process turns, not saved facts/tasks |
| [x] Local/offline commands / دستورهای محلی | Memory/task/file slash commands | No model API request is made |
| [x] Safe configuration / تنظیمات محافظت‌شده | `.env`, `--check`, `/status` | No key output; alias supported; arbitrary API endpoints rejected |
| [x] Local Ollama configuration / تنظیم مدل محلی | Loopback `/v1` + installed model | Config tested offline; local inference untested |
| [x] Continuous task workflow / ادامهٔ خودکار کار | One prompt; approve file writes; inspect `/plan` | Live three-file portfolio completed; empty/partial reply regression passed |
| [x] Completion checks / بررسی پایان | Checklist plus non-empty required files; `finish_work` | Pending steps/missing files rejected; does not prove code correctness |
| [x] Bounded model loop / حلقهٔ محدود | 30 rounds by default; configurable; explicit pause on limit/stall/cancellation | Offline budget, no-progress and cancellation tests passed |
| [x] Crash-resistant state / ذخیرهٔ مقاوم‌تر | Atomic JSON replace + prior-state backup + write lock | Corruption/backup/lock tests passed |
| [x] Secret filtering / فیلتر راز | Known values + common key/password patterns | Offline rejection/redaction tests; not universal detection |
| [ ] Automatic shell/code/test execution / اجرای خودکار کد و تست | Run project tests yourself / تست را خودتان اجرا کنید | Not implemented |
| [ ] Browser/login/JavaScript page automation / کنترل مرورگر | HTML reader only / فقط HTML عمومی | Not implemented |
| [ ] PDF, image, audio ingestion / خواندن PDF و تصویر و صوت | Text/code only / فقط متن و کد | Not implemented |
| [ ] Background schedules and notifications / زمان‌بندی و اعلان | Tasks are a list / کارها فقط فهرست هستند | Not implemented |
| [ ] Unlimited free cloud / cloud رایگان نامحدود | Depends on Ollama account / وابسته به حساب Ollama | Not promised |
| [ ] Guaranteed correct answers/citations / تضمین صحت پاسخ | Review evidence / منبع را بررسی کنید | Model behavior needs human judgment |

Symlink escape checks are implemented; their filesystem creation test was skipped because Windows did not allow symlink creation. A separate mocked resolved-path check covers rejection logic. Web reading blocks private destinations and pins the checked public address before making a TLS connection.

درخواست نمونهٔ تحقیق: «مستندات رسمی Python دربارهٔ list comprehension را پیدا کن، صفحه را بخوان، و سه نکته را با لینک همان منبع توضیح بده.»

درخواست نمونهٔ کدنویسی: «فایل demo.py را بخوان. فقط تابع add را اصلاح کن. قبل از ذخیره تفاوت را نشان بده و بعد بگو خودم با چه دستوری تستش کنم.»
