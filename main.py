"""
main.py
-------
YouTube Live Notifier — Entry Point
====================================
Polls a YouTube channel for live streams and notifies a Telegram channel.

Behaviour
~~~~~~~~~
• Offline → Live  : اگر پیام پایان لایو قبلی وجود دارد حذف شود،
                    سپس یک پیام شروع لایو جدید ارسال شود.
• Still Live      : هیچ کاری نکن (پیام تکراری نفرست).
• Live → Offline  : پیام شروع لایو را حذف کن، پیام پایان ارسال کن.
• Restart recovery: وضعیت از state.json بارگذاری شود.
• Network errors  : لاگ کن و بعد از retry_delay دوباره تلاش کن.
"""

import json
import logging
import os
import sys
import time

from modules.logger import setup_logger
from modules.state_manager import StateManager
from modules.telegram_notifier import TelegramNotifier
from modules.youtube_checker import YouTubeChecker

CONFIG_FILE = "config.json"


def load_config(config_file: str = CONFIG_FILE) -> dict:
    if not os.path.exists(config_file):
        _fatal(
            f"Configuration file '{config_file}' not found.\n"
            "Please create it based on the README instructions."
        )
    try:
        with open(config_file, "r", encoding="utf-8") as fh:
            return json.load(fh)
    except json.JSONDecodeError as exc:
        _fatal(f"'{config_file}' contains invalid JSON: {exc}")


def validate_config(config: dict) -> None:
    required: dict = {
        "youtube_api_key":    "YouTube Data API v3 key",
        "youtube_channel_id": "YouTube Channel ID",
        "telegram_bot_token": "Telegram Bot Token from @BotFather",
        "telegram_chat_id":   "Telegram Chat / Channel ID",
    }
    missing = [
        f"  • {k}  →  {d}"
        for k, d in required.items()
        if not str(config.get(k, "")).strip()
        or str(config.get(k, "")).strip().startswith("YOUR_")
    ]
    if missing:
        _fatal(
            "Missing or unconfigured fields in config.json:\n"
            + "\n".join(missing)
        )


def _fatal(message: str) -> None:
    print(f"\n[FATAL] {message}\n", file=sys.stderr)
    sys.exit(1)


# ── Message builders ───────────────────────────────────────────────────────────

def build_live_message(video_url: str, video_title: str = "", channel_name: str = "") -> str:
    lines = [
        "🔴 <b>لایو شروع شد!</b>\n\n",
        '✨❤️ <a href="https://www.youtube.com/@42LEVEL">YouTube</a>\n'
        '📺 <a href="https://www.aparat.com/42level">آپارات</a>\n',
        '🎮 <a href="https://www.twitch.tv/42level">Twitch</a>\n',
    ]
    if channel_name:
        lines.append(f"📺 کانال: <b>{channel_name}</b>")
    if video_title:
        safe_title = video_title.replace("<", "&lt;").replace(">", "&gt;")
        lines.append(f"🎙 عنوان: <i>{safe_title}</i>")
    lines.append(f'\n▶️ <a href="{video_url}">همین الان ببینید</a>')
    return "\n".join(lines)


def build_end_message() -> str:
    return "🔴 لایو به پایان رسید. از همراهی شما سپاسگزاریم."


# ── Main monitoring loop ───────────────────────────────────────────────────────

def run(config: dict) -> None:
    logger = logging.getLogger("YouTubeLiveNotifier")

    check_interval: int = int(config.get("check_interval_seconds", 300))
    retry_delay: int    = int(config.get("retry_delay_seconds", 15))
    channel_name: str   = config.get("channel_name", "")
    state_file: str     = config.get("state_file", "state.json")

    state = StateManager(state_file=state_file)
    yt    = YouTubeChecker(
        api_key=config["youtube_api_key"],
        channel_id=config["youtube_channel_id"],
    )
    tg    = TelegramNotifier(
        bot_token=config["telegram_bot_token"],
        chat_id=config["telegram_chat_id"],
    )

    logger.info("=" * 65)
    logger.info("  YouTube Live Notifier — Started")
    logger.info(f"  Channel ID      : {config['youtube_channel_id']}")
    logger.info(f"  Channel name    : {channel_name or '(not set)'}")
    logger.info(f"  Check interval  : {check_interval}s")
    logger.info(f"  Retry delay     : {retry_delay}s")
    logger.info(
        f"  Restored state  : is_live={state.is_live}, "
        f"video_id={state.video_id}, "
        f"message_id={state.message_id}, "
        f"end_message_id={state.end_message_id}"
    )
    logger.info("=" * 65)

    while True:
        try:
            known_video_id = state.video_id if state.is_live else None
            is_live, video_id, video_title = yt.check_live(
                current_video_id=known_video_id
            )

            # ── Case 1: Offline → Live ────────────────────────────────
            if is_live and not state.is_live:
                logger.info(
                    f"[TRANSITION] Offline → Live "
                    f"(video_id={video_id}, title='{video_title}')"
                )

                # اگر پیام پایان لایو قبلی هنوز در کانال هست، حذفش کن
                if state.end_message_id:
                    deleted = tg.delete_message(state.end_message_id)
                    if deleted:
                        logger.info(
                            f"Previous end-message deleted "
                            f"(TG message_id={state.end_message_id})."
                        )
                    else:
                        logger.warning(
                            f"Could not delete previous end-message "
                            f"{state.end_message_id}."
                        )

                # ارسال پیام شروع لایو جدید
                video_url   = yt.get_video_url(video_id)
                message_txt = build_live_message(
                    video_url=video_url,
                    video_title=video_title,
                    channel_name=channel_name,
                )
                message_id = tg.send_message(message_txt)

                if message_id:
                    state.set_live(video_id=video_id, message_id=message_id)
                    logger.info(
                        f"Live notification sent. "
                        f"URL={video_url} | TG message_id={message_id}"
                    )
                else:
                    logger.error("Failed to send live notification. Will retry next cycle.")

            # ── Case 2: Still Live — no duplicate ─────────────────────
            elif is_live and state.is_live:
                logger.debug(f"Still live — no action. (video_id={video_id})")

            # ── Case 3: Live → Offline ────────────────────────────────
            elif not is_live and state.is_live:
                logger.info("[TRANSITION] Live → Offline")

                # حذف پیام شروع لایو
                if state.message_id:
                    deleted = tg.delete_message(state.message_id)
                    if deleted:
                        logger.info(
                            f"Live-start message deleted "
                            f"(TG message_id={state.message_id})."
                        )
                    else:
                        logger.warning(
                            f"Could not delete live-start message {state.message_id}."
                        )

                # ارسال پیام پایان لایو و ذخیره message_id آن
                end_msg_id = tg.send_message(build_end_message())
                if end_msg_id:
                    logger.info(
                        f"Live-end notification sent "
                        f"(TG message_id={end_msg_id})."
                    )
                else:
                    logger.error("Failed to send live-end notification.")

                # end_message_id ذخیره می‌شود تا لایو بعدی آن را پاک کند
                state.set_offline(end_message_id=end_msg_id)

            # ── Case 4: Still Offline — no action ─────────────────────
            else:
                logger.debug("Channel is offline — no action.")

            time.sleep(check_interval)

        except KeyboardInterrupt:
            logger.info("Bot stopped by user (Ctrl+C). Goodbye!")
            break

        except Exception as exc:
            logger.warning(
                f"Error in check cycle: {type(exc).__name__}: {exc}. "
                f"Retrying in {retry_delay}s …"
            )
            time.sleep(retry_delay)


# ── Entry point ────────────────────────────────────────────────────────────────

def main() -> None:
    config = load_config()
    validate_config(config)
    setup_logger(
        log_file=config.get("log_file", "bot.log"),
        log_level=config.get("log_level", "INFO"),
    )
    run(config)


if __name__ == "__main__":
    main()
