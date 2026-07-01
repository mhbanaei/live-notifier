"""
main.py — YouTube Live Notifier
================================

Halghe asli:
    Offline → Live  : payam "shoro live" ersal, start_msg_id zakhire
    Live    → Live  : hich kar (payam tekrari narsal)
    Live    → Offline: start_msg_id hazf, payam "payan live" ersal, end_msg_id zakhire
    Offline → Live  : end_msg_id ghobli hazf, baad payam jadid ersal

Ejra:
    python main.py
"""

import json
import logging
import os
import sys
import time

from modules.logger   import setup_logger
from modules.state    import State
from modules.youtube  import YouTubeChecker
from modules.telegram import TelegramBot


def load_config():
    path = os.path.join(os.path.dirname(__file__), "config.json")
    if not os.path.exists(path):
        print(f"[ERROR] config.json not found at: {path}")
        sys.exit(1)
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def validate(cfg):
    required = ["youtube_channel_id", "cookie_file", "telegram_bot_token", "telegram_chat_id"]
    missing  = [k for k in required if not cfg.get(k, "").strip()]
    if missing:
        print(f"[ERROR] Missing fields in config.json: {missing}")
        sys.exit(1)


def live_start_message(video_url, title, channel_name):
    lines = ["🔴 <b>لایو شروع شد!</b>\n"]
    if channel_name:
        lines.append(f"📺 کانال: <b>{channel_name}</b>")
    if title:
        safe = title.replace("<", "&lt;").replace(">", "&gt;")
        lines.append(f"🎙 عنوان: <i>{safe}</i>")
    lines.append(f'\n▶️ <a href="{video_url}">همین الان ببینید</a>')
    return "\n".join(lines)


def live_end_message():
    return "🔴 لایو به پایان رسید. از همراهی شما سپاسگزاریم."


def main():
    cfg = load_config()
    validate(cfg)

    setup_logger(log_level=cfg.get("log_level", "INFO"))
    log = logging.getLogger("YTNotifier")

    check_interval = int(cfg.get("check_interval_seconds", 60))
    retry_delay    = int(cfg.get("retry_delay_seconds", 15))
    channel_name   = cfg.get("channel_name", "")

    yt    = YouTubeChecker(cfg["youtube_channel_id"], cfg["cookie_file"])
    tg    = TelegramBot(cfg["telegram_bot_token"], cfg["telegram_chat_id"])
    state = State()

    log.info("=" * 55)
    log.info("  YouTube Live Notifier started")
    log.info(f"  Channel  : {cfg['youtube_channel_id']}")
    log.info(f"  Name     : {channel_name}")
    log.info(f"  Interval : {check_interval}s")
    log.info(f"  State    : is_live={state.is_live} | start_msg={state.start_msg_id} | end_msg={state.end_msg_id}")
    log.info("=" * 55)

    while True:
        try:
            # Agar ghoblan live bude, haman video ro check kon (sari'tar)
            current_id = state.video_id if state.is_live else None
            is_live, video_id, title = yt.check_live(current_id)

            # ── Offline → Live ────────────────────────────────────────
            if is_live and not state.is_live:
                log.info(f"[TRANSITION] Offline → Live ({video_id})")

                # Payam payan live ghobli ro pak kon
                if state.end_msg_id:
                    tg.delete(state.end_msg_id)

                # Payam shoro live ersal kon
                url  = f"https://www.youtube.com/watch?v={video_id}"
                text = live_start_message(url, title, channel_name)
                mid  = tg.send(text)

                if mid:
                    state.set_live(video_id, mid)
                else:
                    log.error("Failed to send live-start message, will retry next cycle.")

            # ── Live → Live (no action) ───────────────────────────────
            elif is_live and state.is_live:
                log.debug(f"Still live ({video_id}) — no action.")

            # ── Live → Offline ────────────────────────────────────────
            elif not is_live and state.is_live:
                log.info("[TRANSITION] Live → Offline")

                # Payam shoro live ro hazf kon
                tg.delete(state.start_msg_id)

                # Payam payan live ersal kon va end_msg_id ro zakhire kon
                end_mid = tg.send(live_end_message())
                state.set_offline(end_msg_id=end_mid)

            # ── Offline → Offline (no action) ────────────────────────
            else:
                log.debug("Channel offline — no action.")

            time.sleep(check_interval)

        except KeyboardInterrupt:
            log.info("Stopped by user.")
            break

        except Exception as e:
            log.warning(f"Error: {type(e).__name__}: {e} — retrying in {retry_delay}s")
            time.sleep(retry_delay)


if __name__ == "__main__":
    main()
