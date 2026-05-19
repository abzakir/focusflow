"""Analytics view for FocusFlow - premium charts and heatmap."""
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                                QFrame, QScrollArea)
from PySide6.QtCore import Qt, QRectF
from PySide6.QtGui import QFont, QPainter, QColor, QBrush, QPen, QLinearGradient
from datetime import date, timedelta
from utils.helpers import format_hours_minutes


class HeatmapWidget(QWidget):
    """GitHub-style contribution heatmap with premium styling."""

    def __init__(self, db_manager, parent=None):
        super().__init__(parent)
        self.db = db_manager
        self.setMinimumHeight(170)
        self.data = {}
        self._load_data()

    def _load_data(self):
        today = date.today()
        start = today - timedelta(days=90)
        sessions = self.db.get_sessions_range(start.strftime('%Y-%m-%d'), today.strftime('%Y-%m-%d'))
        self.data = {s['date']: s['total_minutes'] for s in sessions}

    def refresh(self):
        self._load_data()
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        cell_size = 13
        gap = 3
        total_size = cell_size + gap
        today = date.today()
        cols = 13
        x_offset = 40
        y_offset = 28

        # Day labels
        painter.setPen(QColor(255, 255, 255, 55))
        painter.setFont(QFont("Segoe UI", 8))
        for i, day in enumerate(["Mon", "", "Wed", "", "Fri", "", ""]):
            if day:
                painter.drawText(2, y_offset + i * total_size + cell_size - 2, day)

        # Month labels
        start_date = today - timedelta(days=90)
        current_month = -1
        for col in range(cols):
            d = start_date + timedelta(days=col * 7)
            if d.month != current_month:
                current_month = d.month
                painter.setPen(QColor(255, 255, 255, 50))
                painter.drawText(x_offset + col * total_size, y_offset - 10, d.strftime("%b"))

        # Draw cells
        for col in range(cols):
            for row in range(7):
                d = start_date + timedelta(days=col * 7 + row)
                if d > today:
                    continue
                x = x_offset + col * total_size
                y = y_offset + row * total_size
                minutes = self.data.get(d.strftime('%Y-%m-%d'), 0)

                color = self._get_heat_color(minutes)
                painter.setBrush(QBrush(color))
                painter.setPen(Qt.PenStyle.NoPen)
                painter.drawRoundedRect(QRectF(x, y, cell_size, cell_size), 3, 3)

        painter.end()

    def _get_heat_color(self, minutes):
        if minutes == 0:
            return QColor(255, 255, 255, 6)
        elif minutes < 30:
            return QColor(108, 99, 255, 50)
        elif minutes < 60:
            return QColor(108, 99, 255, 100)
        elif minutes < 120:
            return QColor(108, 99, 255, 170)
        else:
            return QColor(140, 120, 255, 230)


class BarChartWidget(QWidget):
    """Premium 7-day bar chart."""

    def __init__(self, db_manager, parent=None):
        super().__init__(parent)
        self.db = db_manager
        self.setMinimumHeight(230)
        self.data = []
        self._load_data()

    def _load_data(self):
        today = date.today()
        self.data = []
        for i in range(6, -1, -1):
            d = today - timedelta(days=i)
            d_str = d.strftime('%Y-%m-%d')
            sessions = self.db.get_sessions_range(d_str, d_str)
            minutes = sessions[0]['total_minutes'] if sessions else 0
            self.data.append({'day': d.strftime('%a'), 'date': d_str, 'minutes': minutes})

    def refresh(self):
        self._load_data()
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        w = self.width()
        h = self.height()
        mb = 38
        mt = 24
        ms = 24
        chart_h = h - mb - mt
        chart_w = w - ms * 2

        max_min = max((d['minutes'] for d in self.data), default=60)
        max_min = max(max_min, 30)

        bar_width = min(42, chart_w // (len(self.data) * 2))
        spacing = (chart_w - bar_width * len(self.data)) / (len(self.data) + 1)

        # Grid lines
        painter.setPen(QPen(QColor(255, 255, 255, 12), 1))
        for i in range(4):
            y = mt + chart_h * i / 3
            painter.drawLine(int(ms), int(y), int(w - ms), int(y))

        for i, d in enumerate(self.data):
            x = ms + spacing + i * (bar_width + spacing)
            bar_h = (d['minutes'] / max_min) * chart_h if max_min > 0 else 0
            bar_h = max(bar_h, 3)
            y = mt + chart_h - bar_h

            # Bar with gradient
            grad = QLinearGradient(x, y, x, y + bar_h)
            is_today = (i == len(self.data) - 1)
            if is_today:
                grad.setColorAt(0, QColor("#E040FB"))
                grad.setColorAt(1, QColor("#9D4EDD"))
            else:
                grad.setColorAt(0, QColor(108, 99, 255, 200))
                grad.setColorAt(1, QColor(108, 99, 255, 120))

            painter.setBrush(QBrush(grad))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawRoundedRect(QRectF(x, y, bar_width, bar_h), 6, 6)

            # Soft glow beneath today's bar
            if is_today and d['minutes'] > 0:
                glow = QColor("#E040FB")
                glow.setAlpha(20)
                painter.setBrush(QBrush(glow))
                painter.drawRoundedRect(QRectF(x - 4, y - 4, bar_width + 8, bar_h + 8), 10, 10)

            # Value on top
            painter.setPen(QColor(255, 255, 255, 130))
            painter.setFont(QFont("Segoe UI", 8, QFont.Weight.DemiBold))
            painter.drawText(QRectF(x - 8, y - 20, bar_width + 16, 16),
                             Qt.AlignmentFlag.AlignCenter, f"{d['minutes']:.0f}m")

            # Day label
            painter.setPen(QColor(255, 255, 255, 70 if not is_today else 180))
            painter.setFont(QFont("Segoe UI", 9, QFont.Weight.DemiBold if is_today else QFont.Weight.Normal))
            painter.drawText(QRectF(x - 8, mt + chart_h + 6, bar_width + 16, 22),
                             Qt.AlignmentFlag.AlignCenter, d['day'])

        painter.end()


class AnalyticsView(QWidget):
    """Premium analytics with charts, heatmap, and weekly stats."""

    def __init__(self, db_manager, parent=None):
        super().__init__(parent)
        self.db = db_manager
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

        # Header
        header = QLabel("Analytics")
        header.setObjectName("pageHeader")
        layout.addWidget(header)

        # ── 7-Day Chart Card ──
        chart_frame = self._card()
        chart_layout = QVBoxLayout(chart_frame)
        chart_layout.setContentsMargins(24, 18, 24, 18)
        chart_layout.setSpacing(10)

        chart_header = QHBoxLayout()
        chart_title = QLabel("📊  Last 7 Days")
        chart_title.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        chart_title.setStyleSheet("color: white;")
        chart_header.addWidget(chart_title)
        chart_header.addStretch()
        chart_layout.addLayout(chart_header)

        self.bar_chart = BarChartWidget(self.db)
        chart_layout.addWidget(self.bar_chart)
        layout.addWidget(chart_frame)

        # ── Weekly Stats Row ──
        stats_label = QLabel("WEEKLY SUMMARY")
        stats_label.setObjectName("sectionLabel")
        layout.addWidget(stats_label)

        stats_layout = QHBoxLayout()
        stats_layout.setSpacing(14)

        self.weekly_total = self._stat_box("🕐", "Weekly Total", "0h")
        self.goal_rate = self._stat_box("🎯", "Goal Rate", "0%")
        self.best_day = self._stat_box("⭐", "Best Day", "—")

        stats_layout.addWidget(self.weekly_total)
        stats_layout.addWidget(self.goal_rate)
        stats_layout.addWidget(self.best_day)
        layout.addLayout(stats_layout)

        # ── Heatmap Card ──
        heatmap_frame = self._card()
        hm_layout = QVBoxLayout(heatmap_frame)
        hm_layout.setContentsMargins(24, 18, 24, 18)
        hm_layout.setSpacing(10)

        hm_header = QHBoxLayout()
        hm_title = QLabel("🗓  Activity Heatmap")
        hm_title.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        hm_title.setStyleSheet("color: white;")
        hm_header.addWidget(hm_title)
        hm_header.addStretch()

        period_label = QLabel("Last 90 days")
        period_label.setFont(QFont("Segoe UI", 10))
        period_label.setStyleSheet("color: rgba(255,255,255,0.3);")
        hm_header.addWidget(period_label)
        hm_layout.addLayout(hm_header)

        self.heatmap = HeatmapWidget(self.db)
        hm_layout.addWidget(self.heatmap)

        # Legend
        legend_layout = QHBoxLayout()
        legend_layout.setAlignment(Qt.AlignmentFlag.AlignRight)
        legend_layout.setSpacing(5)
        legend_lbl = QLabel("Less")
        legend_lbl.setStyleSheet("color: rgba(255,255,255,0.3); font-size: 9px;")
        legend_layout.addWidget(legend_lbl)
        for alpha in [6, 50, 100, 170, 230]:
            box = QFrame()
            box.setFixedSize(13, 13)
            box.setStyleSheet(f"background: rgba(108, 99, 255, {alpha}); border-radius: 3px;")
            legend_layout.addWidget(box)
        legend_lbl2 = QLabel("More")
        legend_lbl2.setStyleSheet("color: rgba(255,255,255,0.3); font-size: 9px;")
        legend_layout.addWidget(legend_lbl2)
        hm_layout.addLayout(legend_layout)

        layout.addWidget(heatmap_frame)
        layout.addStretch()

        scroll.setWidget(container)
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(scroll)

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

    def _stat_box(self, icon, label, value):
        frame = QFrame()
        frame.setStyleSheet("""
            QFrame {
                background: rgba(255,255,255,0.025);
                border: 1px solid rgba(255,255,255,0.05);
                border-radius: 16px;
            }
            QFrame:hover {
                background: rgba(255,255,255,0.04);
                border-color: rgba(108,99,255,0.15);
            }
        """)
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(20, 18, 20, 18)
        layout.setSpacing(6)

        icon_lbl = QLabel(icon)
        icon_lbl.setFont(QFont("Segoe UI Emoji", 16))
        icon_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)

        val_label = QLabel(value)
        val_label.setObjectName("val")
        val_label.setFont(QFont("Segoe UI", 20, QFont.Weight.Bold))
        val_label.setStyleSheet("color: #B8B0FF;")
        val_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        txt_label = QLabel(label)
        txt_label.setFont(QFont("Segoe UI", 9))
        txt_label.setStyleSheet("color: rgba(255,255,255,0.35);")
        txt_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(icon_lbl)
        layout.addWidget(val_label)
        layout.addWidget(txt_label)
        return frame

    def refresh(self):
        """Refresh all analytics data."""
        self.bar_chart.refresh()
        self.heatmap.refresh()

        today = date.today()
        week_start = (today - timedelta(days=6)).strftime('%Y-%m-%d')
        week_end = today.strftime('%Y-%m-%d')
        week_data = self.db.get_sessions_range(week_start, week_end)

        weekly_total = sum(s['total_minutes'] for s in week_data) if week_data else 0
        self.weekly_total.findChild(QLabel, "val").setText(format_hours_minutes(weekly_total))

        days_with_goal_met = 0
        for i in range(7):
            d = today - timedelta(days=i)
            goal_data = self.db.get_or_create_daily_goal(d.strftime('%Y-%m-%d'))
            if goal_data['status'] == 'completed':
                days_with_goal_met += 1
        rate = (days_with_goal_met / 7) * 100
        self.goal_rate.findChild(QLabel, "val").setText(f"{rate:.0f}%")

        if week_data:
            best = max(week_data, key=lambda s: s['total_minutes'])
            best_date = date.fromisoformat(best['date'])
            self.best_day.findChild(QLabel, "val").setText(best_date.strftime("%A"))
        else:
            self.best_day.findChild(QLabel, "val").setText("—")
