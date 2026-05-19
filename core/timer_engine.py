"""Timer engine for FocusFlow - manages focus/break timer cycles."""
from PySide6.QtCore import QObject, QTimer, Signal
from datetime import datetime


class TimerEngine(QObject):
    """Core timer engine managing focus and break sessions."""

    # Signals
    tick = Signal(int)           # remaining seconds
    session_started = Signal(str)   # session type
    session_completed = Signal(str, float)  # type, duration_minutes
    state_changed = Signal(str)     # 'running', 'paused', 'idle'
    mode_changed = Signal(str)      # 'focus' or 'break'

    def __init__(self, db_manager, parent=None):
        super().__init__(parent)
        self.db = db_manager
        self._timer = QTimer(self)
        self._timer.setInterval(1000)
        self._timer.timeout.connect(self._on_tick)

        # Configuration
        self.focus_duration = int(self.db.get_setting('focus_duration', '30')) * 60
        self.break_duration = int(self.db.get_setting('break_duration', '5')) * 60
        self.auto_cycle = self.db.get_setting('auto_cycle', 'false') == 'true'
        self.strict_mode = self.db.get_setting('strict_mode', 'false') == 'true'

        # State
        self._remaining = self.focus_duration
        self._total_duration = self.focus_duration
        self._state = 'idle'      # 'idle', 'running', 'paused'
        self._mode = 'focus'       # 'focus', 'break'
        self._session_id = None
        self._elapsed_seconds = 0

    @property
    def remaining(self):
        return self._remaining

    @property
    def total_duration(self):
        return self._total_duration

    @property
    def state(self):
        return self._state

    @property
    def mode(self):
        return self._mode

    @property
    def progress(self):
        """Return progress as 0.0 to 1.0."""
        if self._total_duration == 0:
            return 0.0
        return 1.0 - (self._remaining / self._total_duration)

    def reload_settings(self):
        """Reload durations from database."""
        self.focus_duration = int(self.db.get_setting('focus_duration', '30')) * 60
        self.break_duration = int(self.db.get_setting('break_duration', '5')) * 60
        self.auto_cycle = self.db.get_setting('auto_cycle', 'false') == 'true'
        self.strict_mode = self.db.get_setting('strict_mode', 'false') == 'true'
        if self._state == 'idle':
            self._apply_mode_duration()

    def start(self):
        """Start or resume the timer."""
        if self._state == 'idle':
            self._apply_mode_duration()
            self._elapsed_seconds = 0
            if self._mode == 'focus':
                self._session_id = self.db.start_session('focus')
            self.session_started.emit(self._mode)
        self._state = 'running'
        self._timer.start()
        self.state_changed.emit(self._state)

    def pause(self):
        """Pause the timer."""
        if self._state == 'running':
            self._state = 'paused'
            self._timer.stop()
            self.state_changed.emit(self._state)

    def reset(self):
        """Reset the timer to idle."""
        self._timer.stop()
        self._state = 'idle'
        self._apply_mode_duration()
        self._elapsed_seconds = 0
        self._session_id = None
        self.state_changed.emit(self._state)
        self.tick.emit(self._remaining)

    def skip(self):
        """Skip current session and switch mode."""
        self._timer.stop()
        self._complete_session()

    def set_mode(self, mode):
        """Switch between focus and break."""
        if self._state == 'idle':
            self._mode = mode
            self._apply_mode_duration()
            self.mode_changed.emit(self._mode)
            self.tick.emit(self._remaining)

    def _apply_mode_duration(self):
        if self._mode == 'focus':
            self._remaining = self.focus_duration
            self._total_duration = self.focus_duration
        else:
            self._remaining = self.break_duration
            self._total_duration = self.break_duration

    def _on_tick(self):
        self._remaining -= 1
        self._elapsed_seconds += 1
        self.tick.emit(self._remaining)
        if self._remaining <= 0:
            self._timer.stop()
            self._complete_session()

    def _complete_session(self):
        duration_min = self._elapsed_seconds / 60.0
        session_type = self._mode

        if session_type == 'focus' and self._session_id is not None:
            self.db.end_session(self._session_id, duration_min)
            self.db.update_daily_completed(duration_min)

        self.session_completed.emit(session_type, duration_min)

        # Switch mode
        if self._mode == 'focus':
            self._mode = 'break'
        else:
            self._mode = 'focus'

        self._state = 'idle'
        self._elapsed_seconds = 0
        self._session_id = None
        self._apply_mode_duration()
        self.mode_changed.emit(self._mode)
        self.state_changed.emit(self._state)
        self.tick.emit(self._remaining)

        if self.auto_cycle:
            self.start()
