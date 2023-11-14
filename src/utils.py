"""Utils"""

import sys
from logger import logger


def str2bool(string: str) -> bool:
    """Convert String to Boolean"""

    return string.lower() in ("yes", "on", "true", "1", "y", "ok")


def is_valid_url(url: str | None) -> bool:
    """Check if is URL is not None and safe"""

    if url is None or not url.startswith("https://"):
        return False
    return True


def is_dangerous_regex(pattern: str) -> bool:
    """Check if it is 'dangerous' regex pattern"""

    if ".*" in pattern:
        return True
    return False


def check_pattern(pattern: str, force: bool = False) -> None:
    """Function that checks for dangerous patterns"""

    if is_dangerous_regex(pattern=pattern):
        logger.info(msg=f"Dangerous regex filter pattern detect: '{pattern}'")
        if not force and not str2bool(string=input("Are you sure? (y/n): ")):
            logger.info(msg="Exit...")
            sys.exit(code=0)


def get_percentage(nbr_a: int, nbr_b: int) -> float:
    """Get Percentage"""
    try:
        return nbr_a / nbr_b
    except ZeroDivisionError:
        return 0
