"""Settings view for FocusFlow - premium preferences page."""
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                                QFrame, QSpinBox, QCheckBox, QTimeEdit,
                                QScrollArea, QMessageBox)
from PySide6.QtCore import Qt, QTime, Signal
from PySide6.QtGui import QFont

from ui.components.custom_button import CustomButton


class SettingsView(QWidget):
    """Premium settings page for configuring FocusFlow."""

    settings_changed = Signal()

    def __init__(self, db_manager, parent=None):
        super().__init__(parent)
        self.db = db_manager
        self._setup_ui()
        self._load_settings()

    def _setup_ui(self):
        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setStyleSheet("QScrollArea { background: transparent; border: none; }")

        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(44, 36, 44, 36)
        layout.setSpacing(22)

        # Header
        header = QLabel("Settings")
        header.setObjectName("pageHeader")
        layout.addWidget(header)

        # ── Timer Section ──
        layout.addWidget(self._section_label("TIMER"))
        timer_frame = self._card()
        timer_layout = QVBoxLayout(timer_frame)
        timer_layout.setContentsMargins(24, 20, 24, 20)
        timer_layout.setSpacing(18)

        self.focus_spin = self._spin_row(timer_layout, "Focus Duration (minutes)", 1, 180, 30)
        self.break_spin = self._spin_row(timer_layout, "Break Duration (minutes)", 1, 60, 5)

        self._divider(timer_layout)
        self.auto_cycle_check = self._check_row(timer_layout, "Auto-cycle sessions")
        self.strict_check = self._check_row(timer_layout, "Strict mode — prevent closing during focus")

        layout.addWidget(timer_frame)

        # ── Goals Section ──
        layout.addWidget(self._section_label("GOALS"))
        goal_frame = self._card()
        goal_layout = QVBoxLayout(goal_frame)
        goal_layout.setContentsMargins(24, 20, 24, 20)
        goal_layout.setSpacing(18)

        self.daily_goal_spin = self._spin_row(goal_layout, "Daily Goal (minutes)", 10, 600, 120)
        self.weekend_goal_spin = self._spin_row(goal_layout, "Weekend Goal (minutes)", 10, 600, 60)

        layout.addWidget(goal_frame)

        # ── Notifications & Reminders ──
        layout.addWidget(self._section_label("NOTIFICATIONS"))
        notif_frame = self._card()
        notif_layout = QVBoxLayout(notif_frame)
        notif_layout.setContentsMargins(24, 20, 24, 20)
        notif_layout.setSpacing(18)

        self.notif_check = self._check_row(notif_layout, "Enable notifications")
        self._divider(notif_layout)

        # Reminder time
        time_row = QHBoxLayout()
        time_label = QLabel("Daily Reminder Time")
        time_label.setFont(QFont("Segoe UI", 11))
        time_label.setStyleSheet("color: rgba(255,255,255,0.7);")
        time_row.addWidget(time_label)
        time_row.addStretch()

        self.reminder_time = QTimeEdit()
        self.reminder_time.setDisplayFormat("HH:mm")
        self.reminder_time.setFont(QFont("Segoe UI", 11))
        self.reminder_time.setFixedWidth(120)
        self.reminder_time.setStyleSheet("""
            QTimeEdit {
                background: rgba(255,255,255,0.05);
                border: 1px solid rgba(255,255,255,0.1);
                border-radius: 10px;
                color: white;
                padding: 8px 14px;
            }
            QTimeEdit:focus {
                border-color: rgba(108,99,255,0.4);
            }
            QTimeEdit::up-button, QTimeEdit::down-button {
                background: rgba(255,255,255,0.06);
                border: none;
                width: 22px;
                border-radius: 4px;
            }
            QTimeEdit::up-button:hover, QTimeEdit::down-button:hover {
                background: rgba(255,255,255,0.12);
            }
        """)
        time_row.addWidget(self.reminder_time)
        notif_layout.addLayout(time_row)

        self._divider(notif_layout)
        self.autostart_check = self._check_row(notif_layout, "Launch FocusFlow at Windows startup")

        layout.addWidget(notif_frame)

        # ── Actions ──
        layout.addSpacing(10)
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(14)

        save_btn = CustomButton("💾  Save Settings", variant="primary")
        save_btn.setFixedHeight(48)
        save_btn.clicked.connect(self._save_settings)

        reset_btn = CustomButton("🗑  Reset All Data", variant="danger")
        reset_btn.setFixedHeight(48)
        reset_btn.clicked.connect(self._reset_data)

        btn_layout.addWidget(save_btn)
        btn_layout.addStretch()
        btn_layout.addWidget(reset_btn)
        layout.addLayout(btn_layout)

        layout.addStretch()

        scroll.setWidget(container)
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(scroll)

    def _section_label(self, text):
        label = QLabel(text)
        label.setObjectName("sectionLabel")
        return label

    def _card(self):
        frame = QFrame()
        frame.setStyleSheet("""
            QFrame {
                background: rgba(255,255,255,0.025);
                border: 1px solid rgba(255,255,255,0.05);
                border-radius: 20px;
            }
        """)
        return frame

    def _divider(self, parent_layout):
        line = QFrame()
        line.setFixedHeight(1)
        line.setStyleSheet("background: rgba(255,255,255,0.04);")
        parent_layout.addWidget(line)

    def _spin_row(self, parent_layout, label_text, min_val, max_val, default):
        row = QHBoxLayout()
        label = QLabel(label_text)
        label.setFont(QFont("Segoe UI", 11))
        label.setStyleSheet("color: rgba(255,255,255,0.7);")
        row.addWidget(label)
        row.addStretch()

        spin = QSpinBox()
        spin.setRange(min_val, max_val)
        spin.setValue(default)
        spin.setFont(QFont("Segoe UI", 11))
        spin.setFixedWidth(100)
        spin.setStyleSheet("""
            QSpinBox {
                background: rgba(255,255,255,0.05);
                border: 1px solid rgba(255,255,255,0.1);
                border-radius: 10px;
                color: white;
                padding: 8px 14px;
            }
            QSpinBox:focus {
                border-color: rgba(108,99,255,0.4);
            }
            QSpinBox::up-button, QSpinBox::down-button {
                background: rgba(255,255,255,0.06);
                border: none;
                width: 22px;
                border-radius: 4px;
            }
            QSpinBox::up-button:hover, QSpinBox::down-button:hover {
                background: rgba(255,255,255,0.12);
            }
        """)
        row.addWidget(spin)
        parent_layout.addLayout(row)
        return spin

    def _check_row(self, parent_layout, label_text):
        check = QCheckBox(label_text)
        check.setFont(QFont("Segoe UI", 11))
        check.setStyleSheet("""
            QCheckBox {
                color: rgba(255,255,255,0.7);
                spacing: 12px;
            }
            QCheckBox::indicator {
                width: 22px;
                height: 22px;
                border: 2px solid rgba(255,255,255,0.15);
                border-radius: 6px;
                background: rgba(255,255,255,0.03);
            }
            QCheckBox::indicator:hover {
                border-color: rgba(108,99,255,0.4);
            }
            QCheckBox::indicator:checked {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #6C63FF, stop:1 #9D4EDD);
                border-color: #6C63FF;
            }
        """)
        parent_layout.addWidget(check)
        return check

    def _load_settings(self):
        self.focus_spin.setValue(int(self.db.get_setting('focus_duration', '30')))
        self.break_spin.setValue(int(self.db.get_setting('break_duration', '5')))
        self.daily_goal_spin.setValue(int(self.db.get_setting('daily_goal', '120')))
        self.weekend_goal_spin.setValue(int(self.db.get_setting('weekend_goal', '60')))
        self.auto_cycle_check.setChecked(self.db.get_setting('auto_cycle', 'false') == 'true')
        self.strict_check.setChecked(self.db.get_setting('strict_mode', 'false') == 'true')
        self.autostart_check.setChecked(self.db.get_setting('autostart', 'false') == 'true')
        self.notif_check.setChecked(self.db.get_setting('notifications_permission', 'true') == 'true')

        reminder_str = self.db.get_setting('reminder_time', '09:00')
        parts = reminder_str.split(':')
        self.reminder_time.setTime(QTime(int(parts[0]), int(parts[1])))

    def _save_settings(self):
        self.db.set_setting('focus_duration', str(self.focus_spin.value()))
        self.db.set_setting('break_duration', str(self.break_spin.value()))
        self.db.set_setting('daily_goal', str(self.daily_goal_spin.value()))
        self.db.set_setting('weekend_goal', str(self.weekend_goal_spin.value()))
        self.db.set_setting('auto_cycle', 'true' if self.auto_cycle_check.isChecked() else 'false')
        self.db.set_setting('strict_mode', 'true' if self.strict_check.isChecked() else 'false')
        self.db.set_setting('autostart', 'true' if self.autostart_check.isChecked() else 'false')
        self.db.set_setting('reminder_time', self.reminder_time.time().toString("HH:mm"))
        self.db.set_setting('notifications_permission', 'true' if self.notif_check.isChecked() else 'false')

        self._update_autostart(self.autostart_check.isChecked())

        # Update notification manager if available
        main_win = self.window()
        if hasattr(main_win, 'notifications'):
            main_win.notifications.set_enabled(self.notif_check.isChecked())

        self.settings_changed.emit()

        msg = QMessageBox(self)
        msg.setWindowTitle("FocusFlow")
        msg.setText("✓  Settings saved successfully!")
        msg.exec()

    def _reset_data(self):
        msg = QMessageBox(self)
        msg.setWindowTitle("Reset All Data")
        msg.setText("Are you sure you want to reset ALL data?\n\nThis will delete all sessions, goals, and streaks.\nThis cannot be undone.")
        msg.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if msg.exec() == QMessageBox.StandardButton.Yes:
            self.db.reset_all_data()
            self.settings_changed.emit()

    def _update_autostart(self, enabled):
        import sys, os
        try:
            import winreg
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"Software\Microsoft\Windows\CurrentVersion\Run",
                0, winreg.KEY_SET_VALUE
            )
            if enabled:
                exe_path = sys.executable if getattr(sys, 'frozen', False) else f'"{sys.executable}" "{os.path.abspath(sys.argv[0])}"'
                winreg.SetValueEx(key, "FocusFlow", 0, winreg.REG_SZ, exe_path)
            else:
                try:
                    winreg.DeleteValue(key, "FocusFlow")
                except FileNotFoundError:
                    pass
            winreg.CloseKey(key)
        except Exception:
            pass

    def refresh(self):
        self._load_settings()
