"""Main window for FocusFlow - sidebar navigation and view management."""
from PySide6.QtWidgets import (QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
                                QPushButton, QStackedWidget, QLabel, QFrame,
                                QApplication, QMessageBox, QGraphicsDropShadowEffect)
from PySide6.QtCore import Qt, QSize, QTimer, Slot, QPropertyAnimation, QEasingCurve
from PySide6.QtGui import QFont, QIcon, QCloseEvent, QColor

from database.db_manager import DatabaseManager
from core.timer_engine import TimerEngine
from core.goal_engine import GoalEngine
from core.streak_engine import StreakEngine
from core.reminder_engine import ReminderEngine
from core.music_engine import MusicEngine
from ui.timer_view import TimerView
from ui.dashboard_view import DashboardView
from ui.analytics_view import AnalyticsView
from ui.settings_view import SettingsView
from utils.notifications import NotificationManager


DARK_STYLESHEET = """
/* ══════════════════════════════════════════
   FocusFlow Premium Dark Theme
   ══════════════════════════════════════════ */

QMainWindow {
    background: #0D0B14;
}

QWidget {
    background: transparent;
    color: #E8E6F0;
    font-family: "Segoe UI", sans-serif;
}

/* ── Sidebar ── */
#sidebar {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 #16132A, stop:0.5 #120F22, stop:1 #0D0B14);
    border-right: 1px solid rgba(108, 99, 255, 0.08);
}

#sidebarBtn {
    background: transparent;
    color: rgba(255, 255, 255, 0.40);
    border: none;
    border-radius: 14px;
    padding: 14px 20px;
    text-align: left;
    font-size: 13px;
    font-weight: 500;
    font-family: "Segoe UI";
    margin: 2px 4px;
}

#sidebarBtn:hover {
    background: rgba(108, 99, 255, 0.08);
    color: rgba(255, 255, 255, 0.75);
}

#sidebarBtn[active="true"] {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 rgba(108, 99, 255, 0.18), stop:1 rgba(224, 64, 251, 0.08));
    color: #B8B0FF;
    font-weight: 600;
    border-left: 3px solid #6C63FF;
}

#appTitle {
    color: white;
    font-size: 22px;
    font-weight: 800;
    font-family: "Segoe UI";
    letter-spacing: 1px;
}

#madeBy {
    color: rgba(255, 255, 255, 0.18);
    font-size: 10px;
    font-family: "Segoe UI";
    letter-spacing: 0.5px;
}

/* ── Content Area ── */
#contentArea {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
        stop:0 #0D0B14, stop:0.4 #110E1F, stop:1 #0F0C18);
}

/* ── Scrollbars ── */
QScrollBar:vertical {
    background: transparent;
    width: 6px;
    margin: 0;
}
QScrollBar::handle:vertical {
    background: rgba(108, 99, 255, 0.25);
    border-radius: 3px;
    min-height: 30px;
}
QScrollBar::handle:vertical:hover {
    background: rgba(108, 99, 255, 0.45);
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical,
QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
    background: none;
    border: none;
    height: 0;
}
QScrollBar:horizontal {
    height: 0;
}

/* ── Tooltips ── */
QToolTip {
    background: #1E1A36;
    color: #D0CDE0;
    border: 1px solid rgba(108, 99, 255, 0.2);
    border-radius: 10px;
    padding: 8px 14px;
    font-size: 12px;
}

/* ── Cards / Frames ── */
.card {
    background: rgba(255, 255, 255, 0.025);
    border: 1px solid rgba(255, 255, 255, 0.05);
    border-radius: 20px;
}

/* ── Labels ── */
#pageHeader {
    color: white;
    font-size: 28px;
    font-weight: 800;
    font-family: "Segoe UI";
    letter-spacing: -0.5px;
}

#sectionLabel {
    color: rgba(255, 255, 255, 0.45);
    font-size: 13px;
    font-weight: 600;
    letter-spacing: 2px;
    text-transform: uppercase;
    font-family: "Segoe UI";
}

#subtleText {
    color: rgba(255, 255, 255, 0.35);
    font-size: 11px;
}

/* ── MessageBox ── */
QMessageBox {
    background: #16132A;
}
QMessageBox QLabel {
    color: #E0E0E0;
    font-size: 13px;
}
QMessageBox QPushButton {
    background: #6C63FF;
    color: white;
    border: none;
    border-radius: 10px;
    padding: 8px 24px;
    font-weight: 600;
    min-width: 80px;
}
QMessageBox QPushButton:hover {
    background: #7B73FF;
}
"""


class MainWindow(QMainWindow):
    """Main application window with sidebar navigation."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("FocusFlow")
        self.setMinimumSize(1050, 700)
        self.resize(1150, 780)

        # ── Initialize backend ──
        self.db = DatabaseManager()
        self.timer_engine = TimerEngine(self.db, self)
        self.goal_engine = GoalEngine(self.db)
        self.streak_engine = StreakEngine(self.db)
        self.reminder_engine = ReminderEngine(self.db, self)
        self.music_engine = MusicEngine(self.db, self)

        # ── Apply stylesheet ──
        self.setStyleSheet(DARK_STYLESHEET)

        # ── Build UI ──
        self._setup_ui()
        self._connect_signals()

        # ── Setup notifications (with permission) ──
        self.notifications = NotificationManager(self)

        # Connect reminder engine after notifications setup
        self.reminder_engine.reminder_triggered.connect(self._on_reminder)

        # ── Start engines ──
        self.reminder_engine.start()

        # ── Startup checks ──
        QTimer.singleShot(800, self._startup_checks)

        # ── Auto-refresh timer ──
        self._refresh_timer = QTimer(self)
        self._refresh_timer.setInterval(15000)  # 15 seconds
        self._refresh_timer.timeout.connect(self._refresh_current_view)
        self._refresh_timer.start()

    def _setup_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QHBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # ── Sidebar ──
        sidebar = QFrame()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(230)
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(18, 28, 18, 28)
        sidebar_layout.setSpacing(4)

        # App branding
        brand_layout = QVBoxLayout()
        brand_layout.setSpacing(2)

        title_label = QLabel("⬡ FocusFlow")
        title_label.setObjectName("appTitle")
        brand_layout.addWidget(title_label)

        tagline = QLabel("Stay disciplined")
        tagline.setObjectName("subtleText")
        tagline.setStyleSheet("color: rgba(255,255,255,0.22); font-size: 11px; padding-left: 2px;")
        brand_layout.addWidget(tagline)

        sidebar_layout.addLayout(brand_layout)
        sidebar_layout.addSpacing(35)

        # Nav section label
        nav_label = QLabel("MENU")
        nav_label.setObjectName("sectionLabel")
        nav_label.setStyleSheet("color: rgba(255,255,255,0.2); font-size: 10px; letter-spacing: 3px; padding-left: 8px;")
        sidebar_layout.addWidget(nav_label)
        sidebar_layout.addSpacing(8)

        # Nav buttons
        self.nav_buttons = []
        nav_items = [
            ("🎯   Timer", 0),
            ("📊   Dashboard", 1),
            ("📈   Analytics", 2),
            ("⚙️   Settings", 3),
        ]
        for text, idx in nav_items:
            btn = QPushButton(text)
            btn.setObjectName("sidebarBtn")
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setFixedHeight(48)
            btn.clicked.connect(lambda checked, i=idx: self._switch_page(i))
            sidebar_layout.addWidget(btn)
            self.nav_buttons.append(btn)

        sidebar_layout.addStretch()

        # Bottom branding
        divider = QFrame()
        divider.setFixedHeight(1)
        divider.setStyleSheet("background: rgba(255,255,255,0.05);")
        sidebar_layout.addWidget(divider)
        sidebar_layout.addSpacing(12)

        made_by = QLabel("Made by Zakir")
        made_by.setObjectName("madeBy")
        made_by.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sidebar_layout.addWidget(made_by)

        version_label = QLabel("v1.0.0")
        version_label.setObjectName("madeBy")
        version_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sidebar_layout.addWidget(version_label)

        main_layout.addWidget(sidebar)

        # ── Content Stack ──
        content_wrapper = QWidget()
        content_wrapper.setObjectName("contentArea")
        content_layout = QVBoxLayout(content_wrapper)
        content_layout.setContentsMargins(0, 0, 0, 0)

        self.stack = QStackedWidget()
        self.stack.setStyleSheet("QStackedWidget { background: transparent; }")

        self.timer_view = TimerView(self.timer_engine, self.music_engine)
        self.dashboard_view = DashboardView(self.db, self.goal_engine, self.streak_engine)
        self.analytics_view = AnalyticsView(self.db)
        self.settings_view = SettingsView(self.db)

        self.stack.addWidget(self.timer_view)
        self.stack.addWidget(self.dashboard_view)
        self.stack.addWidget(self.analytics_view)
        self.stack.addWidget(self.settings_view)

        content_layout.addWidget(self.stack)
        main_layout.addWidget(content_wrapper)

        # Start on Timer page
        self._switch_page(0)

    def _connect_signals(self):
        self.timer_engine.session_completed.connect(self._on_session_completed)
        self.timer_engine.session_started.connect(self._on_session_started)
        self.settings_view.settings_changed.connect(self._on_settings_changed)

    def _switch_page(self, index):
        for i, btn in enumerate(self.nav_buttons):
            btn.setProperty("active", i == index)
            btn.style().unpolish(btn)
            btn.style().polish(btn)

        self.stack.setCurrentIndex(index)

        # Refresh the view when switching to it
        current = self.stack.currentWidget()
        if hasattr(current, 'refresh'):
            current.refresh()

    def _refresh_current_view(self):
        current = self.stack.currentWidget()
        if hasattr(current, 'refresh') and current != self.timer_view:
            current.refresh()

    @Slot(str, float)
    def _on_session_completed(self, session_type, duration):
        if session_type == 'focus' and duration > 0:
            status = self.goal_engine.get_today_status()
            if status['is_completed']:
                msg = self.streak_engine.process_day_completion()
                self.notifications.send_celebration(
                    f"Daily goal completed! 🎉 {duration:.0f} min focus session done."
                )
                if msg:
                    self.notifications.send_notification("🏆 Milestone!", msg)
            else:
                self.notifications.send_notification(
                    "Focus Session Complete",
                    f"Great work! {duration:.0f} min focused. {status['remaining_minutes']:.0f} min left to reach your goal."
                )
            self.dashboard_view.refresh()

        # Pause music on session end (break or focus complete)
        self.music_engine.on_focus_ended()

    @Slot(str)
    def _on_session_started(self, session_type):
        if session_type == 'focus':
            self.reminder_engine.mark_session_started()
            self.music_engine.on_focus_started()

    def _on_settings_changed(self):
        self.timer_engine.reload_settings()
        self.dashboard_view.refresh()

    @Slot(str, int)
    def _on_reminder(self, message, reminder_num):
        self.notifications.send_reminder(message)

    def _startup_checks(self):
        """Run startup checks for streaks and missed days."""
        missed_msg = self.streak_engine.process_missed_day()
        if missed_msg:
            self.notifications.send_notification("FocusFlow", missed_msg)
        goal_min = self.goal_engine.get_daily_goal_minutes()
        self.db.get_or_create_daily_goal(default_goal=goal_min)
        self.reminder_engine.reset_daily()

    def closeEvent(self, event: QCloseEvent):
        """Handle window close."""
        if (self.timer_engine.state == 'running' and
                self.timer_engine.mode == 'focus' and
                self.timer_engine.strict_mode):
            event.ignore()
            self.notifications.send_notification(
                "FocusFlow",
                "Strict mode is on. Complete your focus session first!"
            )
            return

        if self.notifications.tray_icon and self.notifications.tray_icon.isVisible():
            event.ignore()
            self.hide()
            self.notifications.send_notification(
                "FocusFlow",
                "App minimized to system tray. Double-click to restore."
            )
        else:
            self.reminder_engine.stop()
            self.db.close()
            event.accept()
