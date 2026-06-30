"""
modules/youtube_checker.py
--------------------------
Wraps the YouTube Data API v3 to detect live streams.

Quota-optimised strategy
~~~~~~~~~~~~~~~~~~~~~~~~
• Searching for a live stream (search.list):  100 quota units per call.
• Confirming a known video is still live (videos.list): 1 quota unit per call.

When the channel is detected as live (we already know the video_id), the
cheaper videos.list call is used. Only when looking for a *new* live stream
do we use the expensive search.list call. This cuts quota usage by up to
99 % during active live streams.

YouTube Data API daily free quota: 10 000 units.
At the default 5-minute check interval, the search.list call costs
10 000 / 100 = 100 calls/day, comfortably within quota for most channels.
"""

import logging
from typing import Optional, Tuple

import requests

logger = logging.getLogger("YouTubeLiveNotifier.YouTube")

# Type alias for readability.
LiveResult = Tuple[bool, Optional[str], str]  # (is_live, video_id, title)


class YouTubeChecker:
    """
    Checks the live-stream status of a YouTube channel.

    Args:
        api_key:    YouTube Data API v3 key.
        channel_id: YouTube channel ID (starts with 'UC…').
    """

    _BASE_URL = "https://www.googleapis.com/youtube/v3"

    def __init__(self, api_key: str, channel_id: str) -> None:
        self.api_key = api_key
        self.channel_id = channel_id
        # Reuse a single TCP connection across requests.
        self._session = requests.Session()
        self._session.headers.update({"User-Agent": "YouTubeLiveNotifier/1.0"})

    # ── Public API ───────────────────────────────────────────────────────

    def check_live(self, current_video_id: Optional[str] = None) -> LiveResult:
        """
        Determine whether the channel is currently broadcasting live.

        When *current_video_id* is supplied (i.e. we already know the
        channel was live in the previous cycle), the cheap videos.list
        endpoint (1 unit) is called to confirm the stream is still active.

        When *current_video_id* is None the more expensive search.list
        endpoint (100 units) is called to detect a new live stream.

        Args:
            current_video_id: Video ID of the previously detected live stream,
                              or None if the channel was offline last cycle.

        Returns:
            Tuple of (is_live, video_id, title).
            video_id and title are None / '' when is_live is False.

        Raises:
            requests.exceptions.RequestException: On network or HTTP errors.
        """
        if current_video_id:
            logger.debug(
                f"Checking known live video {current_video_id} "
                f"via videos.list (1 unit)."
            )
            return self._check_video_live(current_video_id)

        logger.debug("Searching for live streams via search.list (100 units).")
        return self._search_live()

    @staticmethod
    def get_video_url(video_id: str) -> str:
        """Return the canonical YouTube watch URL for *video_id*."""
        return f"https://www.youtube.com/watch?v={video_id}"

    # ── Private helpers ──────────────────────────────────────────────────

    def _search_live(self) -> LiveResult:
        """
        Use search.list to discover an active live stream on the channel.
        Cost: 100 quota units per call.
        """
        params = {
            "part": "id,snippet",
            "channelId": self.channel_id,
            "eventType": "live",
            "type": "video",
            "maxResults": 1,
            "key": self.api_key,
        }

        response = self._session.get(
            f"{self._BASE_URL}/search",
            params=params,
            timeout=15,
        )
        self._handle_api_error(response)

        data = response.json()
        items = data.get("items", [])

        if not items:
            logger.debug("search.list → no active live stream found.")
            return False, None, ""

        item = items[0]
        video_id: str = item["id"]["videoId"]
        title: str = item["snippet"].get("title", "")
        logger.info(f"Live stream detected: '{title}' (video_id={video_id})")
        return True, video_id, title

    def _check_video_live(self, video_id: str) -> LiveResult:
        """
        Use videos.list to check whether a specific video is still live.
        Cost: 1 quota unit per call.
        """
        params = {
            "part": "snippet",
            "id": video_id,
            "key": self.api_key,
        }

        response = self._session.get(
            f"{self._BASE_URL}/videos",
            params=params,
            timeout=15,
        )
        self._handle_api_error(response)

        data = response.json()
        items = data.get("items", [])

        if not items:
            # The video was not returned — it has likely been deleted or ended.
            logger.info(f"videos.list → video {video_id} not found; stream ended.")
            return False, None, ""

        snippet = items[0].get("snippet", {})
        broadcast_content: str = snippet.get("liveBroadcastContent", "none")
        title: str = snippet.get("title", "")

        if broadcast_content == "live":
            logger.debug(
                f"videos.list → video {video_id} is still live ('{title}')."
            )
            return True, video_id, title

        logger.info(
            f"videos.list → video {video_id} is no longer live "
            f"(liveBroadcastContent='{broadcast_content}')."
        )
        return False, None, ""

    @staticmethod
    def _handle_api_error(response: requests.Response) -> None:
        """
        Raise a descriptive error for non-2xx YouTube API responses.

        The YouTube API sometimes returns 4xx / 5xx with a JSON body that
        contains a human-readable 'message' field — include it in the log.
        """
        if response.ok:
            return

        try:
            body = response.json()
            api_msg = (
                body.get("error", {}).get("message", response.text)
            )
        except ValueError:
            api_msg = response.text

        logger.error(
            f"YouTube API error {response.status_code}: {api_msg}"
        )
        response.raise_for_status()  # Re-raise as HTTPError for the caller.
