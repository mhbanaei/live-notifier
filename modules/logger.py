import logging
from logging.handlers import RotatingFileHandler


def setup_logger(log_file="bot.log", log_level="INFO"):
    logger = logging.getLogger("YTNotifier")
    if logger.handlers:
        return logger

    level = getattr(logging, log_level.upper(), logging.INFO)
    logger.setLevel(level)

    fmt = logging.Formatter(
        "%(asctime)s | %(levelname)-8s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Console
    ch = logging.StreamHandler()
    ch.setFormatter(fmt)
    logger.addHandler(ch)

    # File (rotating, max 5MB, 3 backup)
    try:
        fh = RotatingFileHandler(log_file, maxBytes=5*1024*1024, backupCount=3, encoding="utf-8")
        fh.setFormatter(fmt)
        logger.addHandler(fh)
    except OSError:
        logger.warning(f"Cannot open log file '{log_file}', logging to console only.")

    return logger
