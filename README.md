# YouTube Live Notifier

Bot Python ke channel YouTube ro check mikone va kanal Telegram ro update mikone.

---

## Nasbv va Rahandazi

### 1. Nasb dependencies

```bash
pip install -r requirements.txt
```

---

### 2. Gereftane cookies.txt

YouTube request haye bedune login ro block mikone.
Bayad cookies murogar ro export koni:

1. Extension **"Get cookies.txt LOCALLY"** ro to Chrome nasb kon:
   https://chromewebstore.google.com/detail/get-cookiestxt-locally/cclelndahbckbenkjhflpdbgdldlbecc

2. Boro `youtube.com` — login bashi

3. Ru icon extension click kon → **Export as cookies.txt**

4. Fayel `cookies.txt` ro dar khenare `main.py` save kon

---

### 3. Tanzim config.json

```json
{
  "youtube_channel_id": "UCxxxxxxxxxxxxxxxxxx",
  "cookie_file":        "cookies.txt",

  "telegram_bot_token": "123456:AAFxxxxxxxx",
  "telegram_chat_id":   "@your_channel",

  "channel_name":           "Name Channel",
  "check_interval_seconds": 60,
  "retry_delay_seconds":    15,
  "log_level":              "INFO"
}
```

---

### 4. Sakhtane Telegram Bot

1. Be `@BotFather` to Telegram payam bede
2. Dastur `/newbot` ro berfrest
3. Esm va username entekhab kon
4. Token ro copy kon → dar `telegram_bot_token` bezar

**Bot ro Admin kanal kon:**
- Settings → Administrators → Add Administrator
- Username bot ro search kon
- Ezn "Post Messages" va "Delete Messages" ro faal kon

---

### 5. Test ghabel az ejra

```bash
python test_live.py
```

Agar channel offline bood bayad bebini:
```
→ Channel is OFFLINE (normal).
```

---

### 6. Ejra

```bash
python main.py
```

---

## Sakhtare Proje

```
youtube-live-notifier/
├── main.py          ← halghe asli
├── test_live.py     ← bara debug
├── config.json      ← tanzimate (edit kon)
├── cookies.txt      ← az Chrome export kon
├── state.json       ← vazeiat (khودkar sakhe mishe)
├── bot.log          ← log (khودkar sakhe mishe)
├── requirements.txt
└── modules/
    ├── logger.py    ← log giri
    ├── state.py     ← zakhire vazeiat
    ├── youtube.py   ← check live ba yt-dlp
    └── telegram.py  ← ersal/hazf payam
```

---

## Raftare Bot

| Vazeiat | Kar |
|---|---|
| Offline → Live | Payam "live shoro shod" + link ersal |
| Live → Live | Hich (payam tekrari narsal) |
| Live → Offline | Payam shoro hazf + payam "live tamom shod" |
| Live Jadid | Payam payan ghobli hazf + payam shoro jadid |
| Restart | Vazeiat az state.json restore mishe |
| Khata shabake | Log + retry bad az retry_delay saniye |
