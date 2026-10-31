"""Small display helpers shared by the UI."""


def format_duration(seconds) -> str:
    """Format seconds as '45s', '12 min' or '2 h 05 min'."""
    seconds = max(0, int(seconds or 0))
    if seconds < 60:
        return f"{seconds}s"
    minutes = seconds // 60
    if minutes < 60:
        return f"{minutes} min"
    hours, minutes = divmod(minutes, 60)
    return f"{hours} h {minutes:02d} min"


def format_percent(value) -> str:
    return "–" if value is None else f"{round(value)}%"
