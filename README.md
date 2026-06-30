# 🔴 YouTube Live Notifier Bot

ربات پایتون که **به‌صورت خودکار** وضعیت لایو کانال یوتیوب را بررسی کرده و کانال تلگرام را آپدیت می‌کند.

---

## 📌 ویژگی‌ها

| ویژگی | جزئیات |
|---|---|
| بررسی لایو | هر N ثانیه (قابل تنظیم) |
| اطلاع‌رسانی شروع لایو | یک بار + لینک مستقیم |
| حذف پیام شروع پس از پایان | خودکار |
| ارسال پیام پایان لایو | خودکار |
| بازیابی وضعیت پس از ری‌استارت | از `state.json` |
| مقاوم در برابر قطعی اینترنت | بدون توقف |
| بهینه از نظر Quota API | هوشمند (جزئیات پایین) |

---

## 🗂 ساختار پروژه

```
youtube-live-notifier/
├── main.py                    ← نقطه ورودی برنامه
├── config.json                ← تنظیمات (ویرایش کنید)
├── state.json                 ← وضعیت (خودکار ساخته می‌شود)
├── bot.log                    ← فایل لاگ (خودکار ساخته می‌شود)
├── requirements.txt           ← وابستگی‌ها
├── README.md                  ← این فایل
└── modules/
    ├── __init__.py
    ├── logger.py              ← تنظیم لاگ‌گیری
    ├── state_manager.py       ← مدیریت وضعیت پایدار
    ├── youtube_checker.py     ← YouTube Data API v3
    └── telegram_notifier.py   ← Telegram Bot API
```

---

## ⚙️ پیش‌نیازها

- Python 3.9 یا بالاتر
- دسترسی به اینترنت
- اکانت Google (برای YouTube API Key)
- اکانت Telegram

---

## 🚀 راه‌اندازی گام‌به‌گام

---

### مرحله ۱ — دریافت YouTube API Key

1. به آدرس [console.cloud.google.com](https://console.cloud.google.com) بروید.
2. یک **پروژه جدید** بسازید (یا پروژه موجود را انتخاب کنید).
3. از منوی کناری: **APIs & Services → Library**
4. جستجو کنید: **YouTube Data API v3** → کلیک **Enable**
5. از منوی کناری: **APIs & Services → Credentials**
6. کلیک **Create Credentials → API key**
7. کلید ساخته‌شده را کپی کنید — این همان `youtube_api_key` است.

> ⚠️ **نکته امنیتی:** در بخش Credentials روی API key کلیک کرده و زیر
> **API restrictions** فقط دسترسی به `YouTube Data API v3` را مجاز کنید.

---

### مرحله ۲ — پیدا کردن Channel ID کانال یوتیوب

**روش ۱ — از آدرس کانال:**

اگر آدرس کانال شما به این شکل است:
```
https://www.youtube.com/channel/UCxxxxxxxxxxxxxxxxxxxxxxxx
```
رشته بعد از `/channel/` همان Channel ID است (با `UC` شروع می‌شود).

**روش ۲ — از یوتیوب استودیو:**

1. [studio.youtube.com](https://studio.youtube.com) → **Settings → Channel**
2. تب **Advanced settings**
3. مقدار **Channel ID** را کپی کنید.

**روش ۳ — از آدرس‌های `@handle`:**

اگر آدرس به شکل `youtube.com/@username` است، در مرورگر:
1. راست‌کلیک روی صفحه → **View Page Source**
2. جستجو: `"channelId"` — مقدار بعد از آن Channel ID است.

---

### مرحله ۳ — ساخت ربات تلگرام

1. در تلگرام به **@BotFather** پیام دهید.
2. دستور `/newbot` را ارسال کنید.
3. یک **نام** و سپس یک **username** (که باید به `bot` ختم شود) انتخاب کنید.
4. توکن ارسال‌شده را ذخیره کنید — این همان `telegram_bot_token` است.

**اضافه کردن ربات به کانال تلگرام:**

1. وارد کانال تلگرام خود شوید.
2. **Settings → Administrators → Add Administrator**
3. username ربات را جستجو کرده، اضافه کنید.
4. دسترسی‌های مورد نیاز را فعال کنید:
   - ✅ **Post messages** (ارسال پیام)
   - ✅ **Delete messages** (حذف پیام)
5. تأیید کنید.

**پیدا کردن Chat ID کانال:**

- اگر کانال عمومی است: از username کانال استفاده کنید مثلاً `@my_channel`
- اگر کانال خصوصی است: Chat ID عددی آن را نیاز دارید.
  - ربات [@userinfobot](https://t.me/userinfobot) را در تلگرام جستجو کرده و به کانال اضافه کنید تا ID را نمایش دهد.
  - معمولاً به شکل `-100xxxxxxxxxx` است.

---

### مرحله ۴ — نصب پروژه

```bash
# ۱. پوشه پروژه را دریافت کنید (یا از فایل زیپ استخراج کنید)
cd youtube-live-notifier

# ۲. یک محیط مجازی بسازید (توصیه‌شده)
python -m venv venv

# روی Linux / macOS:
source venv/bin/activate

# روی Windows:
venv\Scripts\activate

# ۳. وابستگی‌ها را نصب کنید
pip install -r requirements.txt
```

---

### مرحله ۵ — تنظیم فایل `config.json`

فایل `config.json` را باز کرده و مقادیر را پر کنید:

```json
{
  "youtube_api_key":    "AIza...",
  "youtube_channel_id": "UCxxxxxxxxxxxxxxxxxxxxxxxx",

  "telegram_bot_token": "1234567890:AAFxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
  "telegram_chat_id":   "@my_channel",

  "channel_name": "نام کانال یوتیوب شما",

  "check_interval_seconds": 300,
  "retry_delay_seconds":    15,

  "state_file": "state.json",
  "log_file":   "bot.log",
  "log_level":  "INFO"
}
```

| فیلد | توضیح | پیش‌فرض |
|---|---|---|
| `youtube_api_key` | کلید API یوتیوب | الزامی |
| `youtube_channel_id` | شناسه کانال (با UC شروع می‌شود) | الزامی |
| `telegram_bot_token` | توکن ربات تلگرام | الزامی |
| `telegram_chat_id` | آیدی کانال یا چت تلگرام | الزامی |
| `channel_name` | نام نمایشی کانال در پیام | اختیاری |
| `check_interval_seconds` | فاصله زمانی بررسی (ثانیه) | `300` |
| `retry_delay_seconds` | تأخیر بعد از خطا (ثانیه) | `15` |
| `log_level` | سطح لاگ: DEBUG / INFO / WARNING | `INFO` |

---

### مرحله ۶ — اجرای برنامه

```bash
python main.py
```

برنامه شروع به کار می‌کند و وضعیت را در کنسول و فایل `bot.log` نمایش می‌دهد.

برای توقف: `Ctrl + C`

---

## 🖥 اجرا به‌صورت سرویس (۲۴ ساعته)

### روش اول — Linux با systemd

فایل سرویس بسازید:

```bash
sudo nano /etc/systemd/system/youtube-live-notifier.service
```

محتوا:

```ini
[Unit]
Description=YouTube Live Notifier Bot
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=YOUR_LINUX_USERNAME
WorkingDirectory=/path/to/youtube-live-notifier
ExecStart=/path/to/youtube-live-notifier/venv/bin/python main.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

فعال‌سازی:

```bash
sudo systemctl daemon-reload
sudo systemctl enable youtube-live-notifier
sudo systemctl start youtube-live-notifier

# بررسی وضعیت:
sudo systemctl status youtube-live-notifier

# مشاهده لاگ‌های سرویس:
sudo journalctl -u youtube-live-notifier -f
```

---

### روش دوم — Windows با Task Scheduler

1. `Win + R` → `taskschd.msc`
2. **Create Basic Task…**
3. نام: `YouTube Live Notifier`
4. Trigger: **When the computer starts**
5. Action: **Start a program**
   - Program: `C:\path\to\venv\Scripts\python.exe`
   - Arguments: `main.py`
   - Start in: `C:\path\to\youtube-live-notifier`
6. تیک **Run whether user is logged on or not** را بزنید.
7. تأیید کنید.

---

### روش سوم — `nohup` (Linux، بدون systemd)

```bash
nohup python main.py > /dev/null 2>&1 &
echo $! > bot.pid

# برای توقف:
kill $(cat bot.pid)
```

---

## 📊 مدیریت Quota یوتیوب

YouTube Data API v3 روزانه **۱۰٬۰۰۰ واحد** رایگان دارد.

این پروژه از یک **استراتژی هوشمند** استفاده می‌کند:

| وضعیت کانال | روش بررسی | هزینه |
|---|---|---|
| آفلاین (جستجوی لایو جدید) | `search.list` | **100** واحد |
| لایو (تأیید ادامه لایو) | `videos.list` | **1** واحد |

**محاسبه مصرف با بازه ۵ دقیقه‌ای (پیش‌فرض):**

- حداکثر ۲۸۸ بار جستجو در روز = **۲۸٬۸۰۰ واحد**

> ⚠️ این بیشتر از سهمیه رایگان است. برای ماندن در سقف رایگان:
> - **`check_interval_seconds: 900`** (هر ۱۵ دقیقه) = ۹٬۶۰۰ واحد ✅
> - یا **یک پروژه جداگانه** در Google Cloud با Quota بالاتر درخواست دهید.

اگر کانال شما تقریباً هر روز لایو دارد، بازه ۵ دقیقه مناسب است و Quota کافی است چون بخش عمده‌ای از روز در وضعیت لایو (1 واحد) سپری می‌شود.

---

## 📋 فایل‌های خروجی

| فایل | محتوا |
|---|---|
| `bot.log` | تمام رویدادها، انتقال‌های وضعیت، خطاها |
| `state.json` | وضعیت فعلی: is_live، video_id، message_id |

نمونه `bot.log`:

```
2025-01-15 14:30:00 | INFO     | YouTubeLiveNotifier | ======
2025-01-15 14:30:00 | INFO     | YouTubeLiveNotifier | YouTube Live Notifier — Started
2025-01-15 14:35:00 | INFO     | YouTubeLiveNotifier.YouTube | Live stream detected: 'برنامه ویژه' (video_id=abc123)
2025-01-15 14:35:00 | INFO     | YouTubeLiveNotifier | [TRANSITION] Offline → Live
2025-01-15 14:35:01 | INFO     | YouTubeLiveNotifier.Telegram | Message sent → message_id=1234
2025-01-15 16:05:00 | INFO     | YouTubeLiveNotifier | [TRANSITION] Live → Offline
2025-01-15 16:05:01 | INFO     | YouTubeLiveNotifier.Telegram | Message deleted → message_id=1234
2025-01-15 16:05:02 | INFO     | YouTubeLiveNotifier.Telegram | Message sent → message_id=1235
```

---

## 🔧 عیب‌یابی رایج

| مشکل | راه‌حل |
|---|---|
| `youtube_api_key invalid` | کلید را بررسی کنید؛ API باید فعال باشد |
| `400 Bad Request از Telegram` | مطمئن شوید `telegram_chat_id` صحیح است |
| `403 Forbidden از Telegram` | ربات را به‌عنوان Admin اضافه کنید |
| پیام تکراری ارسال می‌شود | فایل `state.json` را پاک کنید |
| لایو شناسایی نمی‌شود | Channel ID را دوباره بررسی کنید |
| `quotaExceeded` از YouTube | بازه زمانی را افزایش دهید (`check_interval_seconds: 900`) |

---

## 📝 نکات مهم

- **ربات باید admin کانال تلگرام باشد** با دسترسی ارسال و حذف پیام.
- **`config.json`** را هرگز در مخازن عمومی (GitHub و ...) قرار ندهید.
- برای تست اولیه `log_level` را روی `DEBUG` قرار دهید.
- فایل `state.json` را دستی ویرایش نکنید؛ برنامه آن را مدیریت می‌کند.
