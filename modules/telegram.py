"""
Telegram bot — ersal va hazf payam.

Bot bayad Admin kanal bashe ba ezn:
    - Post Messages
    - Delete Messages
"""

import logging

import requests

log = logging.getLogger("YTNotifier.Telegram")


class TelegramBot:
    def __init__(self, token, chat_id):
        self.chat_id  = chat_id
        self.base_url = f"https://api.telegram.org/bot{token}"
        self.session  = requests.Session()

    def send(self, text, parse_mode="HTML"):
        """Payam ersal mikone. message_id ro bar migardone, ya None dar soorat khata."""
        try:
            r = self.session.post(
                f"{self.base_url}/sendMessage",
                json={
                    "chat_id":                  self.chat_id,
                    "text":                     text,
                    "parse_mode":               parse_mode,
                    "disable_web_page_preview": False,
                },
                timeout=15,
            )
            data = r.json()
            if data.get("ok"):
                mid = data["result"]["message_id"]
                log.info(f"Message sent → message_id={mid}")
                return mid
            log.error(f"Telegram sendMessage failed: {data.get('description')}")
            return None
        except Exception as e:
            log.error(f"Telegram send error: {e}")
            return None

    def delete(self, message_id):
        """Payam ro hazf mikone. True/False bar migardone."""
        if not message_id:
            return False
        try:
            r = self.session.post(
                f"{self.base_url}/deleteMessage",
                json={"chat_id": self.chat_id, "message_id": message_id},
                timeout=15,
            )
            data = r.json()
            if data.get("ok"):
                log.info(f"Message deleted → message_id={message_id}")
                return True
            log.warning(f"Telegram deleteMessage failed: {data.get('description')}")
            return False
        except Exception as e:
            log.warning(f"Telegram delete error: {e}")
            return False
