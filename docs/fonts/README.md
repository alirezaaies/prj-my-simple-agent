# Local report fonts / فونت‌های محلی گزارش

## English

Downloaded font binaries stay here locally and are ignored by Git. Free font sources:

- [Vazirmatn](https://github.com/rastikerdar/vazirmatn): Persian/Arabic text; SIL Open Font License 1.1.
- [Noto Sans](https://github.com/notofonts/noto-fonts): English text; SIL Open Font License 1.1.
- [DejaVu Sans Mono](https://github.com/dejavu-fonts/dejavu-fonts): code listings, retrieved from the [Matplotlib font collection](https://github.com/matplotlib/matplotlib/tree/main/lib/matplotlib/mpl-data/fonts/ttf); DejaVu/Bitstream Vera license.

Keep the upstream license terms when redistributing fonts. The project does not redistribute these binaries. `scripts/build_reports.py --download-fonts` can restore the free font files on a fresh checkout. Installed commercial fonts are only fallbacks; no commercial font was copied or redistributed. Change the choices in each language's `config.tex` if needed.

## فارسی

فایل باینری فونت فقط محلی است و وارد Git نمی‌شود. وزیرمتن برای فارسی، Noto Sans برای انگلیسی و DejaVu Sans Mono برای کد استفاده می‌شوند. منبع و مجوز هر کدام در لینک‌های بالا آمده است. هنگام بازنشر فونت شرایط مجوز اصلی را حفظ کنید. فونت تجاری روی سیستم فقط مسیر جایگزین است و کپی نشده است. برای بازیابی فونت رایگان دستور بالا را اجرا کنید؛ برای تغییر انتخاب، config.tex هر زبان را ویرایش کنید.
