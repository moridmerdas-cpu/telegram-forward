# robot_view — ربات فوروارد با اشتراک زمانی (برای Render)

این پروژه نسخهٔ آماده برای دیپلوی روی **Render.com** است.  
ویژگی‌ها:
- دریافت آپدیت‌ها از تلگرام با **Webhook** (مناسب Render)
- ذخیره‌سازی کاربران و اشتراک‌ها در SQLite
- پرداخت از طریق درگاه ایرانی (نمونه: IDPay / Pay.ir)
- Dockerfile برای اجرای کانتینری
- GitHub Actions workflow که بعد از push، یک Deploy جدید روی Render تریگر می‌کند

## مراحل سریع برای راه‌اندازی

1. یک Repository در GitHub بساز و این پروژه را push کن.
2. در Render یک Web Service بساز و GitHub repository را متصل کن **یا** از GitHub Actions استفاده کن (مراحل پایین).
3. در Settings → Environment Variables در Render یا GitHub Secrets این مقادیر را ست کن:
   - BOT_TOKEN
   - ADMIN_ID
   - DATABASE_PATH (مثلاً data.db)
   - PAYMENT_PROVIDER (idpay یا payir)
   - IDPAY_API_KEY
   - BASE_URL (آدرس سرویس Render مثل https://yourservice.onrender.com)
   - RENDER_SERVICE_ID (برای GitHub Actions، آیدی سرویس روی Render)
   - RENDER_API_KEY (برای GitHub Actions، API Key در Render - Account → API Keys)
4. اگر از Render با Dockerfile استفاده می‌کنی، Render خودکار build و deploy انجام می‌دهد.
5. بعد از اولین دیپلوی، webhook تلگرام را ست کن:
   ```
   curl -F "url=https://yourservice.onrender.com/telegram" https://api.telegram.org/bot<YOUR_BOT_TOKEN>/setWebhook
   ```
   یا از اسکریپت `set_webhook.sh` استفاده کن.

## فایل‌های مهم
- `main.py` : اپ Flask که هم callback تلگرام و هم callback پرداخت را دریافت می‌کند و منطق اصلی را دارد.
- `database.py` : مدیریت SQLite
- `Dockerfile` : برای ساخت ایمیج Docker
- `.github/workflows/deploy.yml` : GitHub Actions workflow که Deploy را روی Render تریگر می‌کند
- `set_webhook.sh` : اسکریپتی برای ست کردن webhook

## نکات امنیتی
- هرگز توکن‌ها و کلیدها را داخل کد نریز؛ از environment variables استفاده کن.
- قبل از باز کردن ربات روی کانال/گروه واقعی، در گروه‌های تستی امتحان کن.
- رعایت محدودیت‌های تلگرام در ارسال پیام و فوروارد مهم است.

اگر تمایل داشتی من می‌تونم:
- webhook handler را کامل‌تر کنم (verification, logging)
- یا یک نسخه‌ی Docker Compose و نمونه‌ی Deploy مستقیم روی Render بسازم.
