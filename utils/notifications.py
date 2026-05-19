"""Windows notification utilities for FocusFlow with permission dialog."""
import sys
import os

from PySide6.QtWidgets import (QSystemTrayIcon, QMenu, QApplication,
                                QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                                QPushButton, QCheckBox, QFrame)
from PySide6.QtGui import QIcon, QFont, QPixmap, QColor, QPainter
from PySide6.QtCore import Qt
from utils.helpers import get_resource_path


class NotificationPermissionDialog(QDialog):
    """Beautiful dialog asking for notification permission."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("FocusFlow — Notifications")
        self.setFixedSize(420, 320)
        self.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self._result = False
        self._setup_ui()

    def _setup_ui(self):
        # Outer card with rounded corners
        card = QFrame(self)
        card.setGeometry(0, 0, 420, 320)
        card.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #1E1A36, stop:1 #14112A);
                border: 1px solid rgba(108, 99, 255, 0.2);
                border-radius: 20px;
            }
        """)

        layout = QVBoxLayout(card)
        layout.setContentsMargins(32, 32, 32, 28)
        layout.setSpacing(16)

        # Bell icon
        icon_label = QLabel("🔔")
        icon_label.setFont(QFont("Segoe UI Emoji", 36))
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(icon_label)

        # Title
        title = QLabel("Enable Notifications?")
        title.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        title.setStyleSheet("color: white;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        # Description
        desc = QLabel(
            "FocusFlow can send you study reminders, session alerts,\n"
            "and milestone celebrations via Windows notifications."
        )
        desc.setFont(QFont("Segoe UI", 10))
        desc.setStyleSheet("color: rgba(255,255,255,0.55);")
        desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        desc.setWordWrap(True)
        layout.addWidget(desc)

        layout.addSpacing(8)

        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(12)

        deny_btn = QPushButton("Not Now")
        deny_btn.setFont(QFont("Segoe UI", 11, QFont.Weight.DemiBold))
        deny_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        deny_btn.setFixedHeight(44)
        deny_btn.setStyleSheet("""
            QPushButton {
                background: rgba(255,255,255,0.06);
                color: rgba(255,255,255,0.6);
                border: 1px solid rgba(255,255,255,0.1);
                border-radius: 12px;
                padding: 0 24px;
            }
            QPushButton:hover {
                background: rgba(255,255,255,0.1);
                color: white;
            }
        """)
        deny_btn.clicked.connect(self._deny)

        allow_btn = QPushButton("✓  Allow Notifications")
        allow_btn.setFont(QFont("Segoe UI", 11, QFont.Weight.DemiBold))
        allow_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        allow_btn.setFixedHeight(44)
        allow_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #6C63FF, stop:1 #9D4EDD);
                color: white;
                border: none;
                border-radius: 12px;
                padding: 0 28px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #7B73FF, stop:1 #AC5EEE);
            }
        """)
        allow_btn.clicked.connect(self._allow)

        btn_layout.addWidget(deny_btn)
        btn_layout.addWidget(allow_btn)
        layout.addLayout(btn_layout)

    def _allow(self):
        self._result = True
        self.accept()

    def _deny(self):
        self._result = False
        self.accept()

    @property
    def notifications_allowed(self):
        return self._result


class NotificationManager:
    """Manages system tray and toast notifications with permission."""

    def __init__(self, parent=None):
        self.parent = parent
        self.tray_icon = None
        self._notifications_enabled = False
        self._check_permission()
        self._setup_tray()

    def _check_permission(self):
        """Check if notifications are permitted, ask if first time."""
        from database.db_manager import DatabaseManager
        if hasattr(self.parent, 'db'):
            db = self.parent.db
        else:
            db = DatabaseManager()

        perm = db.get_setting('notifications_permission')
        if perm is None:
            # First launch — ask permission
            dialog = NotificationPermissionDialog(self.parent)
            dialog.exec()
            allowed = dialog.notifications_allowed
            db.set_setting('notifications_permission', 'true' if allowed else 'false')
            self._notifications_enabled = allowed
        else:
            self._notifications_enabled = (perm == 'true')

    def _setup_tray(self):
        """Setup system tray icon."""
        if not QSystemTrayIcon.isSystemTrayAvailable():
            return
        self.tray_icon = QSystemTrayIcon(self.parent)

        # Set icon from Logo.png
        logo_path = get_resource_path('Logo.png')
        if os.path.exists(logo_path):
            self.tray_icon.setIcon(QIcon(logo_path))
        else:
            app = QApplication.instance()
            if app:
                self.tray_icon.setIcon(app.windowIcon())

        # Context menu
        menu = QMenu()
        menu.setStyleSheet("""
            QMenu {
                background: #1E1A36;
                border: 1px solid rgba(108,99,255,0.2);
                border-radius: 10px;
                padding: 6px;
            }
            QMenu::item {
                padding: 8px 24px;
                color: rgba(255,255,255,0.8);
                border-radius: 6px;
                font-size: 12px;
            }
            QMenu::item:selected {
                background: rgba(108,99,255,0.2);
                color: white;
            }
        """)

        show_action = menu.addAction("🔵  Show FocusFlow")
        show_action.triggered.connect(self._show_window)
        menu.addSeparator()
        quit_action = menu.addAction("✕  Quit")
        quit_action.triggered.connect(self._quit_app)

        self.tray_icon.setContextMenu(menu)
        self.tray_icon.activated.connect(self._on_tray_activated)
        self.tray_icon.show()

    def _show_window(self):
        if self.parent:
            self.parent.showNormal()
            self.parent.activateWindow()
            self.parent.raise_()

    def _quit_app(self):
        if hasattr(self.parent, 'db'):
            self.parent.db.close()
        QApplication.instance().quit()

    def _on_tray_activated(self, reason):
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            self._show_window()

    def send_notification(self, title, message, duration=5000):
        """Send a system tray notification (if permitted)."""
        if not self._notifications_enabled:
            return
        if self.tray_icon and self.tray_icon.isVisible():
            self.tray_icon.showMessage(
                title, message,
                QSystemTrayIcon.MessageIcon.Information,
                duration
            )

    def send_reminder(self, message):
        """Send a study reminder notification."""
        self.send_notification("FocusFlow Reminder", message, 8000)

    def send_celebration(self, message):
        """Send a celebration notification."""
        self.send_notification("🎉 FocusFlow", message, 6000)

    def set_enabled(self, enabled):
        """Enable or disable notifications."""
        self._notifications_enabled = enabled
        if hasattr(self.parent, 'db'):
            self.parent.db.set_setting('notifications_permission', 'true' if enabled else 'false')
