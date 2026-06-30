"""
modules/telegram_notifier.py
-----------------------------
Wraps the Telegram Bot HTTP API for sending and deleting messages.

Uses the synchronous 'requests' library directly (no third-party SDK)
so there are no extra dependencies and the code stays simple.

Bot permissions required in the target channel
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
• Post messages  (to send live-start / live-end notifications)
• Delete messages (to remove the live-start notification when the stream ends)

Both permissions must be granted when adding the bot as a channel administrator.
"""

import logging
from typing import Optional

import requests

logger = logging.getLogger("YouTubeLiveNotifier.Telegram")


class TelegramNotifier:
    """
    Sends and deletes messages in a Telegram chat or channel.

    Args:
        bot_token: The HTTP API token obtained from @BotFather.
        chat_id:   Target chat identifier.
                   For public channels: '@channel_username'
                   For private chats or channels: numeric ID (e.g. '-100123456789').
    """

    def __init__(self, bot_token: str, chat_id: str) -> None:
        self.chat_id = chat_id
        self._base_url = f"https://api.telegram.org/bot{bot_token}"
        self._session = requests.Session()
        self._session.headers.update({"User-Agent": "YouTubeLiveNotifier/1.0"})

    # ── Public API ───────────────────────────────────────────────────────

    def send_message(
        self,
        text: str,
        parse_mode: str = "HTML",
        disable_web_page_preview: bool = False,
    ) -> Optional[int]:
        """
        Send a text message to the configured chat.

        Args:
            text:                     Message body. HTML tags are supported.
            parse_mode:               Telegram parse mode ('HTML' or 'Markdown').
            disable_web_page_preview: When True, link previews are suppressed.

        Returns:
            The Telegram message_id on success, or None on failure.

        Raises:
            requests.exceptions.RequestException: On network errors.
        """
        payload = {
            "chat_id": self.chat_id,
            "text": text,
            "parse_mode": parse_mode,
            "disable_web_page_preview": disable_web_page_preview,
        }

        response = self._session.post(
            f"{self._base_url}/sendMessage",
            json=payload,
            timeout=15,
        )

        data = self._parse_response(response, action="sendMessage")
        if data is None:
            return None

        message_id: int = data["result"]["message_id"]
        logger.info(f"Message sent → message_id={message_id}")
        return message_id

    def delete_message(self, message_id: int) -> bool:
        """
        Delete a previously sent message.

        Args:
            message_id: The Telegram message ID to delete.

        Returns:
            True on success, False on failure (does not raise).
        """
        payload = {
            "chat_id": self.chat_id,
            "message_id": message_id,
        }

        try:
            response = self._session.post(
                f"{self._base_url}/deleteMessage",
                json=payload,
                timeout=15,
            )
            data = self._parse_response(response, action="deleteMessage")
            if data and data.get("result") is True:
                logger.info(f"Message deleted → message_id={message_id}")
                return True
        except requests.exceptions.RequestException as exc:
            logger.warning(
                f"Network error while deleting message {message_id}: {exc}"
            )

        return False

    # ── Internal helpers ─────────────────────────────────────────────────

    def _parse_response(
        self, response: requests.Response, action: str
    ) -> Optional[dict]:
        """
        Parse a Telegram API response, log any errors, and return the JSON
        body on success or None on failure.

        Args:
            response: The raw HTTP response.
            action:   API method name (for logging only).

        Returns:
            Parsed JSON dict on success, None on failure.

        Raises:
            requests.exceptions.RequestException: On HTTP-level errors for
            actions other than deleteMessage (to surface them to the caller).
        """
        try:
            data: dict = response.json()
        except ValueError:
            logger.error(
                f"Telegram {action}: non-JSON response "
                f"(HTTP {response.status_code})."
            )
            response.raise_for_status()
            return None

        if data.get("ok"):
            return data

        # Telegram returned ok=false with an error description.
        description: str = data.get("description", "Unknown error")
        error_code: int = data.get("error_code", response.status_code)
        logger.error(
            f"Telegram {action} failed [{error_code}]: {description}"
        )

        # For sendMessage, propagate failures so the caller can decide
        # whether to retry.  For deleteMessage, return None silently.
        if action == "sendMessage":
            response.raise_for_status()

        return None
