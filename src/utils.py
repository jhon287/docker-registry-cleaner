"""Utils"""


def str2bool(string: str) -> bool:
    """Convert String to Boolean"""

    return string.lower() in ("yes", "on", "true", "1", "y", "ok")


def is_valid_url(url: str) -> bool:
    """Check if is URL is not None and safe"""

    if not url or not url.startswith("https://"):
        return False
    return True


def is_dangerous_regex(pattern: str) -> bool:
    """Check if it is 'dangerous' regex pattern"""

    if ".*" in pattern:
        return True
    return False


def get_percentage(nbr_a: int, nbr_b: int) -> float:
    """Get Percentage"""
    try:
        return nbr_a / nbr_b
    except ZeroDivisionError:
        return 0
