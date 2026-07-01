"""
YouTube live checker — ba yt-dlp va cookies.txt.

Chera cookies.txt?
    YouTube requests bedune login ro block mikone (429).
    Ba export kardan cookies az murogar, yt-dlp mesle
    yek karbar واقعی dide mishavad.

Chetor kar mikone:
    - Safheye /live kanal ro check mikone.
    - YouTube in safhe ro be live faal redirect mikone.
    - yt-dlp az field haye is_live va live_status estefade mikone.
    - Agar live nabash, DownloadError mide ke handle mishe.
"""

import logging

import yt_dlp

log = logging.getLogger("YTNotifier.YouTube")


class YouTubeChecker:
    def __init__(self, channel_id, cookie_file="cookies.txt"):
        self.channel_url = f"https://www.youtube.com/channel/{channel_id}/live"
        self.opts = {
            "quiet":                   True,
            "no_warnings":             True,
            "skip_download":           True,
            "ignore_no_formats_error": True,
            "cookiefile":              cookie_file,
        }
        log.info(f"YouTubeChecker ready | channel_url={self.channel_url} | cookie_file={cookie_file}")

    def check_live(self, current_video_id=None):
        """
        Returns: (is_live: bool, video_id: str|None, title: str)

        Agar current_video_id darim, haman video ro check mikonim (sari'tar).
        Dar gheyr e in, safheye /live kanal ro check mikonim.
        """
        url = (
            f"https://www.youtube.com/watch?v={current_video_id}"
            if current_video_id
            else self.channel_url
        )

        try:
            with yt_dlp.YoutubeDL(self.opts) as ydl:
                info = ydl.extract_info(url, download=False)

            if not info:
                log.debug("No info returned from yt-dlp.")
                return False, None, ""

            video_id    = info.get("id", "")
            title       = info.get("title", "")
            is_live     = bool(info.get("is_live"))
            live_status = info.get("live_status") or ""

            log.debug(f"yt-dlp → id={video_id!r} is_live={is_live} live_status={live_status!r} title={title!r}")

            if is_live or live_status == "is_live":
                log.info(f"LIVE detected: '{title}' (id={video_id})")
                return True, video_id, title

            return False, None, ""

        except yt_dlp.utils.DownloadError as e:
            err = str(e).lower()
            # In ha hame yani channel offline ast — normal ast
            if any(p in err for p in [
                "not currently live",
                "this live event will begin",
                "no video formats found",
                "video unavailable",
                "private video",
                "members-only",
            ]):
                log.debug(f"Channel offline: {str(e).strip()}")
                return False, None, ""
            # Khtaye dige ro be halghe asli pass bede ta retry beshe
            raise
