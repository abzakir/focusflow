"""Dashboard view for FocusFlow - premium daily overview."""
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                                QFrame, QProgressBar, QGridLayout, QScrollArea)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

from ui.components.stat_card import StatCard
from utils.helpers import format_hours_minutes


class DashboardView(QWidget):
    """Premium dashboard with daily goal progress, streaks, and stats."""

    def __init__(self, db_manager, goal_engine, streak_engine, parent=None):
        super().__init__(parent)
        self.db = db_manager
        self.goal_engine = goal_engine
        self.streak_engine = streak_engine
        self._setup_ui()

    def _setup_ui(self):
        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setStyleSheet("QScrollArea { background: transparent; border: none; }")

        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(44, 36, 44, 36)
        layout.setSpacing(24)

        # ── Header ──
        header_layout = QHBoxLayout()
        header = QLabel("Dashboard")
        header.setObjectName("pageHeader")
        header_layout.addWidget(header)
        header_layout.addStretch()

        # Today indicator
        from datetime import date
        today_label = QLabel(date.today().strftime("%A, %B %d"))
        today_label.setFont(QFont("Segoe UI", 11))
        today_label.setStyleSheet("color: rgba(255,255,255,0.3);")
        header_layout.addWidget(today_label)
        layout.addLayout(header_layout)

        # ── Goal Card ──
        goal_frame = QFrame()
        goal_frame.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 rgba(108,99,255,0.08), stop:1 rgba(224,64,251,0.04));
                border: 1px solid rgba(108,99,255,0.12);
                border-radius: 20px;
            }
        """)
        goal_layout = QVBoxLayout(goal_frame)
        goal_layout.setContentsMargins(28, 24, 28, 24)
        goal_layout.setSpacing(14)

        # Goal header row
        goal_header = QHBoxLayout()
        goal_icon_title = QHBoxLayout()
        goal_icon_title.setSpacing(10)
        goal_icon = QLabel("🎯")
        goal_icon.setFont(QFont("Segoe UI Emoji", 18))
        goal_icon_title.addWidget(goal_icon)
        goal_title = QLabel("Today's Goal")
        goal_title.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        goal_title.setStyleSheet("color: white;")
        goal_icon_title.addWidget(goal_title)
        goal_header.addLayout(goal_icon_title)
        goal_header.addStretch()

        self.goal_percentage_label = QLabel("0%")
        self.goal_percentage_label.setFont(QFont("Segoe UI", 26, QFont.Weight.Bold))
        self.goal_percentage_label.setStyleSheet("color: #6C63FF;")
        goal_header.addWidget(self.goal_percentage_label)
        goal_layout.addLayout(goal_header)

        # Progress bar
        self.goal_progress = QProgressBar()
        self.goal_progress.setFixedHeight(12)
        self.goal_progress.setTextVisible(False)
        self._set_progress_style("#6C63FF", "#E040FB")
        goal_layout.addWidget(self.goal_progress)

        # Goal details
        details_layout = QHBoxLayout()
        self.completed_label = QLabel("0m completed")
        self.completed_label.setFont(QFont("Segoe UI", 10))
        self.completed_label.setStyleSheet("color: rgba(255,255,255,0.4);")

        self.remaining_label = QLabel("120m remaining")
        self.remaining_label.setFont(QFont("Segoe UI", 10))
        self.remaining_label.setStyleSheet("color: rgba(255,255,255,0.4);")

        details_layout.addWidget(self.completed_label)
        details_layout.addStretch()
        details_layout.addWidget(self.remaining_label)
        goal_layout.addLayout(details_layout)

        # Motivational text
        self.motivation_label = QLabel("")
        self.motivation_label.setFont(QFont("Segoe UI", 12))
        self.motivation_label.setStyleSheet("color: rgba(255,255,255,0.55);")
        self.motivation_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        goal_layout.addWidget(self.motivation_label)

        layout.addWidget(goal_frame)

        # ── Stats Section ──
        stats_label = QLabel("OVERVIEW")
        stats_label.setObjectName("sectionLabel")
        layout.addWidget(stats_label)

        cards_grid = QGridLayout()
        cards_grid.setSpacing(14)

        self.streak_card = StatCard("🔥", "0", "Current Streak", "#FF6B6B")
        self.longest_card = StatCard("⚡", "0", "Longest Streak", "#FFD93D")
        self.today_card = StatCard("📚", "0m", "Today's Focus", "#B8B0FF")
        self.total_card = StatCard("🏆", "0h", "Total Hours", "#E040FB")
        self.sessions_card = StatCard("📊", "0", "Total Sessions", "#00C9A7")
        self.consistency_card = StatCard("📈", "0%", "Consistency", "#00D4FF")

        cards_grid.addWidget(self.streak_card, 0, 0)
        cards_grid.addWidget(self.longest_card, 0, 1)
        cards_grid.addWidget(self.today_card, 0, 2)
        cards_grid.addWidget(self.total_card, 1, 0)
        cards_grid.addWidget(self.sessions_card, 1, 1)
        cards_grid.addWidget(self.consistency_card, 1, 2)

        layout.addLayout(cards_grid)

        # ── Behavioral Message ──
        self.behavioral_frame = QFrame()
        self.behavioral_frame.setStyleSheet("""
            QFrame {
                background: rgba(108, 99, 255, 0.06);
                border: 1px solid rgba(108, 99, 255, 0.15);
                border-radius: 16px;
            }
        """)
        self.behavioral_label = QLabel("")
        self.behavioral_label.setFont(QFont("Segoe UI", 11))
        self.behavioral_label.setStyleSheet("color: rgba(255,255,255,0.65);")
        self.behavioral_label.setWordWrap(True)
        self.behavioral_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        beh_layout = QVBoxLayout(self.behavioral_frame)
        beh_layout.setContentsMargins(24, 18, 24, 18)
        beh_layout.addWidget(self.behavioral_label)
        self.behavioral_frame.setVisible(False)
        layout.addWidget(self.behavioral_frame)

        layout.addStretch()

        scroll.setWidget(container)
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(scroll)

    def _set_progress_style(self, color1, color2):
        self.goal_progress.setStyleSheet(f"""
            QProgressBar {{
                background: rgba(255,255,255,0.05);
                border: none;
                border-radius: 6px;
            }}
            QProgressBar::chunk {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {color1}, stop:1 {color2});
                border-radius: 6px;
            }}
        """)

    def refresh(self):
        """Update all dashboard data."""
        status = self.goal_engine.get_today_status()
        pct = min(status['percentage'], 100)
        self.goal_progress.setValue(int(pct))
        self.goal_percentage_label.setText(f"{status['percentage']:.0f}%")
        self.completed_label.setText(f"{format_hours_minutes(status['completed_minutes'])} completed")
        self.remaining_label.setText(f"{format_hours_minutes(status['remaining_minutes'])} remaining")
        self.motivation_label.setText(status['motivational_text'])

        color = self.goal_engine.get_color_hex(status['color_state'])
        cs = status['color_state']
        if cs == 'gold':
            self._set_progress_style("#FFD700", "#FFA500")
            self.goal_percentage_label.setStyleSheet("color: #FFD700;")
        elif cs == 'green':
            self._set_progress_style("#6BCB77", "#2ECC71")
            self.goal_percentage_label.setStyleSheet("color: #6BCB77;")
        elif cs == 'yellow':
            self._set_progress_style("#FFD93D", "#F39C12")
            self.goal_percentage_label.setStyleSheet("color: #FFD93D;")
        elif cs == 'red':
            self._set_progress_style("#FF6B6B", "#E74C3C")
            self.goal_percentage_label.setStyleSheet("color: #FF6B6B;")
        else:
            self._set_progress_style("#6C63FF", "#E040FB")
            self.goal_percentage_label.setStyleSheet("color: #6C63FF;")

        # Streak data
        streak_data = self.streak_engine.get_streak_data()
        self.streak_card.update_value(str(streak_data['current_streak']))
        self.longest_card.update_value(str(streak_data['longest_streak']))
        self.consistency_card.update_value(f"{streak_data['consistency_percent']:.0f}%")

        today_min = self.db.get_total_minutes_today()
        self.today_card.update_value(format_hours_minutes(today_min))
        total_hours = self.db.get_total_focus_hours()
        self.total_card.update_value(f"{total_hours:.1f}h")
        self.sessions_card.update_value(str(self.db.get_total_sessions()))

        # Behavioral message
        msg_type, msg = self.streak_engine.get_behavioral_message()
        if msg:
            self.behavioral_label.setText(msg)
            self.behavioral_frame.setVisible(True)
            if msg_type == 'warning':
                self.behavioral_frame.setStyleSheet("""
                    QFrame {
                        background: rgba(255, 107, 107, 0.06);
                        border: 1px solid rgba(255, 107, 107, 0.15);
                        border-radius: 16px;
                    }
                """)
            else:
                self.behavioral_frame.setStyleSheet("""
                    QFrame {
                        background: rgba(108, 99, 255, 0.06);
                        border: 1px solid rgba(108, 99, 255, 0.15);
                        border-radius: 16px;
                    }
                """)
        else:
            self.behavioral_frame.setVisible(False)
