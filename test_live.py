"""
test_live.py — bara debug

Ejra:
    python test_live.py

Khorooji ro bebeen:
    - Agar channel offline bood: DownloadError ya "Not live"
    - Agar channel live bood: is_live=True va title ro neshon mide
"""

import json
import yt_dlp

with open("config.json", encoding="utf-8") as f:
    cfg = json.load(f)

channel_id  = cfg["youtube_channel_id"]
cookie_file = cfg["cookie_file"]
url         = f"https://www.youtube.com/channel/{channel_id}/live"

print(f"Channel  : {channel_id}")
print(f"Cookies  : {cookie_file}")
print(f"URL      : {url}")
print("-" * 50)

opts = {
    "quiet":                   False,
    "no_warnings":             False,
    "skip_download":           True,
    "ignore_no_formats_error": True,
    "cookiefile":              cookie_file,
}

try:
    with yt_dlp.YoutubeDL(opts) as ydl:
        info = ydl.extract_info(url, download=False)

    if info:
        print("\n=== RESULT ===")
        for k in ["id", "title", "is_live", "live_status", "was_live"]:
            print(f"  {k:15}: {info.get(k)!r}")
    else:
        print("No info returned.")

except yt_dlp.utils.DownloadError as e:
    print(f"\nDownloadError: {e}")
    if "not currently live" in str(e).lower():
        print("\n→ Channel is OFFLINE (normal).")
except Exception as e:
    print(f"\nError: {type(e).__name__}: {e}")
