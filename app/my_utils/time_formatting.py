from datetime import datetime, timezone, timedelta
from typing import Union

def format_timestamp(dt: Union[datetime, None]) -> str:
    """
    Converts a datetime (with or without timezone) into human-readable format
    Examples:
        Just now → if < 1 min ago
        5m ago   → if < 1 hour
        2h ago   → if today
        Yesterday at 3:45 PM
        19 Nov 2025, 4:00 PM
    """
    if not dt:
        return "N/A"

    # Ensure it's timezone-aware (has timezone info)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    else:
        dt = dt.astimezone(timezone.utc)

    now = datetime.now(timezone.utc)
    diff = now - dt

    if diff.total_seconds() < 60:
        return "Just now"
    elif diff.total_seconds() < 3600:
        mins = int(diff.total_seconds() // 60)
        return f"{mins}m ago"
    elif diff.days == 0:  # Today
        return dt.astimezone(get_local_indian_time()).strftime("Today at %I:%M %p")
    elif diff.days == 1:
        return dt.astimezone(get_local_indian_time()).strftime("Yesterday at %I:%M %p")
    elif diff.days < 7:
        return dt.astimezone(get_local_indian_time()).strftime("%A at %I:%M %p")  # Monday at 4:00 PM
    else:
        return dt.astimezone(get_local_indian_time()).strftime("%d-%m-%Y %I:%M %p")


def get_local_indian_time():
    """Returns IST timezone (UTC +5:30)"""
    return timezone(timedelta(hours=5, minutes=30))