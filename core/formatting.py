"""Small display helpers shared by the UI."""
from core.i18n import tr


def format_duration(seconds) -> str:
    """Format seconds as '45s', '12 min' or '2 h 05 min'."""
    seconds = max(0, int(seconds or 0))
    if seconds < 60:
        return tr("{seconds}s", seconds=seconds)
    minutes = seconds // 60
    if minutes < 60:
        return tr("{minutes} min", minutes=minutes)
    hours, minutes = divmod(minutes, 60)
    return tr("{hours} h {minutes:02d} min", hours=hours, minutes=minutes)


def format_percent(value) -> str:
    return "–" if value is None else f"{round(value)}%"
