# Report continuation rules / قواعد ادامهٔ گزارش

## English

Read all four original `agent-guidelines/` files before extending reports. Keep English first and Persian second in README files. Use matching chapter structure, accent color and page geometry in both reports. Use XeLaTeX; Persian requires `xepersian` loaded after direction-sensitive packages and at least 1.5 line spacing. Put Latin phrases on separate source lines in `\lr{}` and whole code blocks in `LTR`.

Explain concrete setup, commands, expected output, errors, and why each module exists. Include current public source with wrapped code listings. Never copy `.env`, real state, headers, keys, or unredacted network errors. Separate offline test evidence, live evidence and untested behavior. Preserve the precise author name and all six original contact URLs on the cover, each page footer, and final contact section; confirm PDF annotation destinations. Use a `.bib` file and numbered IEEE references. Keep downloaded fonts/images and generated artifacts ignored. Compile, inspect warnings, render pages, inspect margins and footer spacing, and update `PROJECT_STATUS.md` after changes.

## فارسی

قبل از تکمیل، چهار فایل اصلی `agent-guidelines/` را بخوانید. ساختار فصل‌ها، رنگ و حاشیهٔ دو زبان یکسان باشد. برای فارسی از `xepersian` و فاصلهٔ خطوط حداقل ۱٫۵ استفاده کنید. متن لاتین در منبع روی خط مستقل با `\lr{}` و بلوک کد در محیط `LTR` قرار بگیرد.

نصب و دستورها و خروجی مورد انتظار و رفع خطا را قدم‌به‌قدم توضیح دهید. علت وجود هر ماژول را بنویسید و کد عمومی فعلی را در ضمیمهٔ دارای شکست سطر بیاورید. محتوای `.env`، حافظهٔ واقعی، کلید یا خطای شبکهٔ حاوی اطلاعات محرمانه ممنوع است. آزمون محلی و واقعی و رفتار تست‌نشده را دقیق تفکیک کنید. نام کامل و شش لینک اصلی نویسنده روی جلد و پاورقی همهٔ صفحات و بخش پایانی حفظ شوند؛ مقصد لینک در PDF هم بررسی شود. منابع در `.bib` با قالب شماره‌دار IEEE باشند. فونت و تصاویر و خروجی تولیدی وارد Git نشوند. بعد از ساخت، هشدارها و تصویر صفحات و حاشیه و پاورقی را بررسی و وضعیت پروژه را ثبت کنید.
