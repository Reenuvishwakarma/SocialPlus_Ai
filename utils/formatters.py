"""
SocialPulse AI - Number and Text Formatters
Utility functions for formatting numbers, percentages, dates, and text.
"""
from datetime import datetime, date
from typing import Optional, Union


def format_number(n: Union[int, float, None], decimals: int = 0) -> str:
    """Format number with compact notation (1.2K, 1.2M, etc.)."""
    if n is None:
        return "N/A"
    try:
        n = float(n)
    except (ValueError, TypeError):
        return "N/A"

    if abs(n) >= 1_000_000_000:
        return f"{n / 1_000_000_000:.1f}B"
    elif abs(n) >= 1_000_000:
        return f"{n / 1_000_000:.1f}M"
    elif abs(n) >= 1_000:
        return f"{n / 1_000:.1f}K"
    else:
        if decimals == 0:
            return f"{int(n):,}"
        return f"{n:,.{decimals}f}"


def format_number_full(n: Union[int, float, None]) -> str:
    """Format number with full comma separation."""
    if n is None:
        return "N/A"
    try:
        n = float(n)
        if n == int(n):
            return f"{int(n):,}"
        return f"{n:,.2f}"
    except (ValueError, TypeError):
        return "N/A"


def format_percentage(val: Union[float, None], decimals: int = 1, include_sign: bool = False) -> str:
    """Format value as percentage string."""
    if val is None:
        return "N/A"
    try:
        val = float(val)
        sign = "+" if include_sign and val > 0 else ""
        return f"{sign}{val:.{decimals}f}%"
    except (ValueError, TypeError):
        return "N/A"


def format_change(current: Union[float, None], previous: Union[float, None]) -> dict:
    """
    Calculate and format change between two values.
    Returns dict with value, percentage, direction, color, arrow.
    """
    result = {
        "value": 0,
        "percentage": 0,
        "direction": "neutral",
        "color": "#767586",
        "arrow": "→",
        "label": "No change",
        "available": False,
    }

    if current is None or previous is None:
        return result

    try:
        current = float(current)
        previous = float(previous)
    except (ValueError, TypeError):
        return result

    result["available"] = True
    diff = current - previous

    if previous != 0:
        pct = ((current - previous) / abs(previous)) * 100
    elif current != 0:
        pct = 100.0
    else:
        pct = 0.0

    result["value"] = diff
    result["percentage"] = round(pct, 1)

    if diff > 0:
        result["direction"] = "up"
        result["color"] = "#00885D"
        result["arrow"] = "↑"
        result["label"] = f"+{format_percentage(pct, include_sign=False)}"
    elif diff < 0:
        result["direction"] = "down"
        result["color"] = "#DC3545"
        result["arrow"] = "↓"
        result["label"] = f"{format_percentage(pct)}"
    else:
        result["direction"] = "neutral"
        result["label"] = "0%"

    return result


def format_date(dt: Union[str, datetime, date, None], fmt: str = "%b %d, %Y") -> str:
    """Format a date value to readable string."""
    if dt is None:
        return "N/A"
    if isinstance(dt, str):
        try:
            dt = datetime.fromisoformat(dt.replace("Z", "+00:00"))
        except ValueError:
            try:
                from pandas import to_datetime
                dt = to_datetime(dt)
            except Exception:
                return str(dt)
    try:
        return dt.strftime(fmt)
    except (AttributeError, ValueError):
        return str(dt)


def format_date_range(start, end) -> str:
    """Format date range as 'Aug 1 - Aug 30, 2024'."""
    start_str = format_date(start, "%b %d")
    end_str = format_date(end, "%b %d, %Y")
    return f"{start_str} – {end_str}"


def truncate_text(text: Optional[str], max_len: int = 50) -> str:
    """Truncate text with ellipsis."""
    if not text:
        return "Untitled Post"
    text = str(text).strip()
    if len(text) <= max_len:
        return text
    return text[:max_len - 3] + "..."


def ordinal(n: int) -> str:
    """Return ordinal string for number (1st, 2nd, 3rd, etc.)."""
    if 11 <= (n % 100) <= 13:
        suffix = "th"
    else:
        suffix = {1: "st", 2: "nd", 3: "rd"}.get(n % 10, "th")
    return f"{n}{suffix}"
