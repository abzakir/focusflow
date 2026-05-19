"""Custom styled button widget for FocusFlow."""
from PySide6.QtWidgets import QPushButton
from PySide6.QtCore import Qt, QPropertyAnimation, QEasingCurve, Property, QSize
from PySide6.QtGui import QColor, QFont, QCursor


class CustomButton(QPushButton):
    """A modern styled button with hover effects."""

    def __init__(self, text="", parent=None, variant="primary"):
        super().__init__(text, parent)
        self._variant = variant
        self.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.setMinimumHeight(44)
        self.setFont(QFont("Segoe UI", 11, QFont.Weight.DemiBold))
        self._apply_style()

    def _apply_style(self):
        styles = {
            'primary': """
                QPushButton {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                        stop:0 #6C63FF, stop:1 #E040FB);
                    color: white;
                    border: none;
                    border-radius: 12px;
                    padding: 10px 28px;
                    font-weight: 600;
                }
                QPushButton:hover {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                        stop:0 #7B73FF, stop:1 #E858FF);
                }
                QPushButton:pressed {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                        stop:0 #5A52E0, stop:1 #C030DB);
                }
                QPushButton:disabled {
                    background: #3A3A4A;
                    color: #666;
                }
            """,
            'secondary': """
                QPushButton {
                    background: rgba(255, 255, 255, 0.08);
                    color: #CCC;
                    border: 1px solid rgba(255,255,255,0.12);
                    border-radius: 12px;
                    padding: 10px 28px;
                    font-weight: 600;
                }
                QPushButton:hover {
                    background: rgba(255, 255, 255, 0.14);
                    color: white;
                    border-color: rgba(255,255,255,0.2);
                }
                QPushButton:pressed {
                    background: rgba(255,255,255,0.05);
                }
            """,
            'danger': """
                QPushButton {
                    background: rgba(255, 80, 80, 0.15);
                    color: #FF6B6B;
                    border: 1px solid rgba(255, 80, 80, 0.3);
                    border-radius: 12px;
                    padding: 10px 28px;
                    font-weight: 600;
                }
                QPushButton:hover {
                    background: rgba(255, 80, 80, 0.25);
                    border-color: rgba(255, 80, 80, 0.5);
                }
                QPushButton:pressed {
                    background: rgba(255, 80, 80, 0.1);
                }
            """,
            'success': """
                QPushButton {
                    background: rgba(107, 203, 119, 0.15);
                    color: #6BCB77;
                    border: 1px solid rgba(107, 203, 119, 0.3);
                    border-radius: 12px;
                    padding: 10px 28px;
                    font-weight: 600;
                }
                QPushButton:hover {
                    background: rgba(107, 203, 119, 0.25);
                    border-color: rgba(107, 203, 119, 0.5);
                }
                QPushButton:pressed {
                    background: rgba(107, 203, 119, 0.1);
                }
            """,
            'icon': """
                QPushButton {
                    background: rgba(255, 255, 255, 0.06);
                    color: #AAA;
                    border: none;
                    border-radius: 10px;
                    padding: 8px;
                    font-size: 16px;
                }
                QPushButton:hover {
                    background: rgba(255, 255, 255, 0.12);
                    color: white;
                }
            """,
        }
        self.setStyleSheet(styles.get(self._variant, styles['primary']))

    def set_variant(self, variant):
        self._variant = variant
        self._apply_style()
