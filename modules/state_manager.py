"""
modules/state_manager.py
------------------------
Persists the bot's runtime state (is_live, video_id, message_id,
end_message_id) to a JSON file so that the correct state is restored
after a restart and duplicate notifications are never sent.
"""

import json
import logging
import os
from typing import Optional

logger = logging.getLogger("YouTubeLiveNotifier.StateManager")


class StateManager:
    """
    Manages reading and writing of the bot's operational state.

    State fields
    ------------
    is_live        : bool       – Whether the channel is currently live.
    video_id       : str | None – YouTube video ID of the active live stream.
    message_id     : int | None – Telegram message ID of the live-start notification.
    end_message_id : int | None – Telegram message ID of the live-end notification
                                  (deleted when the next live starts).
    """

    _DEFAULT_STATE: dict = {
        "is_live": False,
        "video_id": None,
        "message_id": None,
        "end_message_id": None,
    }

    def __init__(self, state_file: str = "state.json") -> None:
        self.state_file = state_file
        self._state: dict = self._load()

    # ── Persistence helpers ──────────────────────────────────────────────

    def _load(self) -> dict:
        """Load state from disk; fall back to default on any error."""
        if not os.path.exists(self.state_file):
            logger.info("No state file found — starting with default state.")
            return dict(self._DEFAULT_STATE)

        try:
            with open(self.state_file, "r", encoding="utf-8") as fh:
                data = json.load(fh)
            merged = {**self._DEFAULT_STATE, **data}
            logger.info(
                f"State loaded from '{self.state_file}': "
                f"is_live={merged['is_live']}, "
                f"video_id={merged['video_id']}, "
                f"message_id={merged['message_id']}, "
                f"end_message_id={merged['end_message_id']}"
            )
            return merged
        except (json.JSONDecodeError, OSError) as exc:
            logger.warning(
                f"Could not load state file '{self.state_file}': {exc}. "
                "Using default state."
            )
            return dict(self._DEFAULT_STATE)

    def _save(self) -> None:
        """Write current state to disk."""
        try:
            with open(self.state_file, "w", encoding="utf-8") as fh:
                json.dump(self._state, fh, indent=2, ensure_ascii=False)
        except OSError as exc:
            logger.error(f"Could not save state to '{self.state_file}': {exc}")

    # ── Property accessors ───────────────────────────────────────────────

    @property
    def is_live(self) -> bool:
        return bool(self._state.get("is_live", False))

    @property
    def video_id(self) -> Optional[str]:
        return self._state.get("video_id")

    @property
    def message_id(self) -> Optional[int]:
        return self._state.get("message_id")

    @property
    def end_message_id(self) -> Optional[int]:
        return self._state.get("end_message_id")

    # ── State transition helpers ─────────────────────────────────────────

    def set_live(self, video_id: str, message_id: int) -> None:
        """Record that the channel has gone live."""
        self._state["is_live"] = True
        self._state["video_id"] = video_id
        self._state["message_id"] = message_id
        self._state["end_message_id"] = None   # پیام پایان قدیمی دیگر معتبر نیست
        self._save()
        logger.info(
            f"State → LIVE | video_id={video_id} | message_id={message_id}"
        )

    def set_offline(self, end_message_id: Optional[int] = None) -> None:
        """
        Record that the live stream has ended.

        Args:
            end_message_id: Telegram message ID of the just-sent end notification,
                            stored so it can be deleted when the next live starts.
        """
        self._state["is_live"] = False
        self._state["video_id"] = None
        self._state["message_id"] = None
        self._state["end_message_id"] = end_message_id
        self._save()
        logger.info(f"State → OFFLINE | end_message_id={end_message_id}")

    def __repr__(self) -> str:
        return (
            f"StateManager("
            f"is_live={self.is_live}, "
            f"video_id={self.video_id!r}, "
            f"message_id={self.message_id}, "
            f"end_message_id={self.end_message_id})"
        )
