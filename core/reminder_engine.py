"""Reminder engine for FocusFlow - scheduled study reminders."""
from PySide6.QtCore import QObject, QTimer, Signal
from datetime import datetime, date


class ReminderEngine(QObject):
    """Manages scheduled reminders with escalation."""

    reminder_triggered = Signal(str, int)  # message, reminder_number

    def __init__(self, db_manager, parent=None):
        super().__init__(parent)
        self.db = db_manager
        self._check_timer = QTimer(self)
        self._check_timer.setInterval(60000)  # Check every minute
        self._check_timer.timeout.connect(self._check_reminders)
        self._reminders_sent_today = 0
        self._reminder_times = [0, 20, 60]  # minutes after set time
        self._started_session_today = False

    def start(self):
        """Start the reminder checking loop."""
        self._check_timer.start()

    def stop(self):
        self._check_timer.stop()

    def mark_session_started(self):
        """Mark that a session was started today - suppress further reminders."""
        self._started_session_today = True

    def reset_daily(self):
        """Reset daily state - call at midnight or app start."""
        self._reminders_sent_today = 0
        self._started_session_today = False

    def _check_reminders(self):
        if self._started_session_today:
            return

        reminder_time_str = self.db.get_setting('reminder_time', '09:00')
        try:
            now = datetime.now()
            parts = reminder_time_str.split(':')
            scheduled_hour = int(parts[0])
            scheduled_min = int(parts[1])
            scheduled = now.replace(hour=scheduled_hour, minute=scheduled_min, second=0)

            # Only send reminders after scheduled time
            if now < scheduled:
                return

            minutes_late = (now - scheduled).total_seconds() / 60

            # Determine which reminder to send
            for i, threshold in enumerate(self._reminder_times):
                if i >= self._reminders_sent_today and minutes_late >= threshold:
                    self._send_reminder(i, minutes_late)
                    break

        except (ValueError, IndexError):
            pass

    def _send_reminder(self, reminder_num, delay_minutes):
        messages = [
            "⏰ Time to start your focus session!",
            "📚 Hey! You haven't started studying yet. Let's go!",
            "🔔 Final reminder: Don't let today slip away. Even a short session counts!",
        ]
        if reminder_num < len(messages):
            self.reminder_triggered.emit(messages[reminder_num], reminder_num)
            self._reminders_sent_today = reminder_num + 1
            self.db.log_reminder(date.today().strftime('%Y-%m-%d'), delay_minutes)
