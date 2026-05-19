"""Helper utilities for FocusFlow."""
import os
import sys


def get_resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller."""
    if hasattr(sys, '_MEIPASS'):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)


def format_time(seconds):
    """Format seconds into MM:SS string."""
    minutes = int(seconds) // 60
    secs = int(seconds) % 60
    return f"{minutes:02d}:{secs:02d}"


def format_hours_minutes(total_minutes):
    """Format minutes into Xh Ym string."""
    hours = int(total_minutes) // 60
    mins = int(total_minutes) % 60
    if hours > 0:
        return f"{hours}h {mins}m"
    return f"{mins}m"


def get_app_data_dir():
    """Get the application data directory."""
    app_data = os.path.join(os.getenv('APPDATA', '.'), 'FocusFlow')
    os.makedirs(app_data, exist_ok=True)
    return app_data


def is_weekend():
    """Check if today is a weekend."""
    from datetime import date
    return date.today().weekday() >= 5
