"""
State manager — vazeiat bot ro dar state.json zakhire mikone.

Fields:
    is_live        : aya channel alan live hast
    video_id       : video_id live faal
    start_msg_id   : telegram message_id payam "live shoro shod"
    end_msg_id     : telegram message_id payam "live tamom shod"
                     (ta live baadi pak beshe)
"""

import json
import logging
import os

log = logging.getLogger("YTNotifier.State")

DEFAULT = {
    "is_live":      False,
    "video_id":     None,
    "start_msg_id": None,
    "end_msg_id":   None,
}

STATE_FILE = "state.json"


def _load():
    if not os.path.exists(STATE_FILE):
        log.info("No state file found, starting fresh.")
        return dict(DEFAULT)
    try:
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        state = {**DEFAULT, **data}
        log.info(f"State loaded: {state}")
        return state
    except Exception as e:
        log.warning(f"Could not load state: {e} — starting fresh.")
        return dict(DEFAULT)


def _save(state):
    try:
        with open(STATE_FILE, "w", encoding="utf-8") as f:
            json.dump(state, f, indent=2)
    except Exception as e:
        log.error(f"Could not save state: {e}")


class State:
    def __init__(self):
        self._s = _load()

    # ── Getters ──────────────────────────────────────────────────────────

    @property
    def is_live(self):
        return self._s["is_live"]

    @property
    def video_id(self):
        return self._s["video_id"]

    @property
    def start_msg_id(self):
        return self._s["start_msg_id"]

    @property
    def end_msg_id(self):
        return self._s["end_msg_id"]

    # ── Transitions ──────────────────────────────────────────────────────

    def set_live(self, video_id, start_msg_id):
        self._s = {
            "is_live":      True,
            "video_id":     video_id,
            "start_msg_id": start_msg_id,
            "end_msg_id":   None,
        }
        _save(self._s)
        log.info(f"State → LIVE | video_id={video_id} | start_msg_id={start_msg_id}")

    def set_offline(self, end_msg_id=None):
        self._s = {
            "is_live":      False,
            "video_id":     None,
            "start_msg_id": None,
            "end_msg_id":   end_msg_id,
        }
        _save(self._s)
        log.info(f"State → OFFLINE | end_msg_id={end_msg_id}")
