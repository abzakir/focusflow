"""Stat card widget for FocusFlow dashboard - premium version."""
from PySide6.QtWidgets import QFrame, QVBoxLayout, QLabel
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont


class StatCard(QFrame):
    """A premium glassmorphism card with icon, value, and label."""

    def __init__(self, icon="📊", value="0", label="Stat", accent_color="#6C63FF", parent=None):
        super().__init__(parent)
        self._accent = accent_color
        self.setObjectName("statCardFrame")
        self.setStyleSheet(f"""
            #statCardFrame {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 rgba(255,255,255,0.035),
                    stop:1 rgba(255,255,255,0.015));
                border: 1px solid rgba(255, 255, 255, 0.06);
                border-radius: 18px;
            }}
            #statCardFrame:hover {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 rgba(255,255,255,0.06),
                    stop:1 rgba(255,255,255,0.025));
                border-color: {accent_color}30;
            }}
        """)
        self.setMinimumWidth(165)
        self.setMinimumHeight(140)

        layout = QVBoxLayout(self)
        layout.setSpacing(6)
        layout.setContentsMargins(20, 20, 20, 20)

        # Icon
        self.icon_label = QLabel(icon)
        self.icon_label.setFont(QFont("Segoe UI Emoji", 20))
        self.icon_label.setAlignment(Qt.AlignmentFlag.AlignLeft)

        # Value
        self.value_label = QLabel(str(value))
        self.value_label.setFont(QFont("Segoe UI", 26, QFont.Weight.Bold))
        self.value_label.setStyleSheet(f"color: {accent_color};")
        self.value_label.setAlignment(Qt.AlignmentFlag.AlignLeft)

        # Label
        self.label_label = QLabel(label)
        self.label_label.setFont(QFont("Segoe UI", 9))
        self.label_label.setStyleSheet("color: rgba(255,255,255,0.35);")
        self.label_label.setAlignment(Qt.AlignmentFlag.AlignLeft)

        layout.addWidget(self.icon_label)
        layout.addSpacing(2)
        layout.addWidget(self.value_label)
        layout.addWidget(self.label_label)
        layout.addStretch()

    def update_value(self, value):
        self.value_label.setText(str(value))

    def update_label(self, label):
        self.label_label.setText(label)

    def update_icon(self, icon):
        self.icon_label.setText(icon)
