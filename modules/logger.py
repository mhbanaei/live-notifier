"""
modules/logger.py
-----------------
Configures the application-wide logger with both a console handler
and a rotating file handler. Importing this module and calling
setup_logger() once is all that is required.
"""

import logging
from logging.handlers import RotatingFileHandler


def setup_logger(
    log_file: str = "bot.log",
    log_level: str = "INFO",
    max_bytes: int = 5 * 1024 * 1024,  # 5 MB
    backup_count: int = 3,
) -> logging.Logger:
    """
    Create and configure the root application logger.

    Args:
        log_file:     Path to the log file.
        log_level:    Minimum logging level ('DEBUG', 'INFO', 'WARNING', 'ERROR').
        max_bytes:    Maximum size of each log file before rotation.
        backup_count: Number of rotated log files to keep.

    Returns:
        The configured Logger instance.
    """
    logger = logging.getLogger("YouTubeLiveNotifier")

    # Avoid adding duplicate handlers when called more than once.
    if logger.handlers:
        return logger

    level = getattr(logging, log_level.upper(), logging.INFO)
    logger.setLevel(level)

    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)-40s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # ── Console handler ──────────────────────────────────────────────────
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # ── Rotating file handler ────────────────────────────────────────────
    try:
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=max_bytes,
            backupCount=backup_count,
            encoding="utf-8",
        )
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    except OSError as exc:
        logger.warning(f"Could not open log file '{log_file}': {exc}. Logging to console only.")

    return logger
