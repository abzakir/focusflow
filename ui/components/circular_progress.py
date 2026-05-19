"""Circular progress ring widget for FocusFlow timer - premium version."""
from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Qt, QRectF, Property, QPropertyAnimation, QEasingCurve
from PySide6.QtGui import QPainter, QPen, QColor, QConicalGradient, QFont, QRadialGradient, QBrush


class CircularProgress(QWidget):
    """A premium animated circular progress ring with glow effects."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(300, 300)
        self.setMaximumSize(380, 380)

        self._value = 0.0
        self._max_value = 1.0
        self._text = "00:00"
        self._sub_text = "FOCUS"
        self._ring_color_start = QColor("#6C63FF")
        self._ring_color_end = QColor("#E040FB")
        self._bg_ring_color = QColor(255, 255, 255, 12)
        self._ring_width = 10
        self._animation = None

    def get_value(self):
        return self._value

    def set_value(self, val):
        self._value = val
        self.update()

    value = Property(float, get_value, set_value)

    def set_colors(self, start_hex, end_hex):
        self._ring_color_start = QColor(start_hex)
        self._ring_color_end = QColor(end_hex)
        self.update()

    def set_text(self, text):
        self._text = text
        self.update()

    def set_sub_text(self, text):
        self._sub_text = text
        self.update()

    def animate_to(self, target_value, duration=500):
        if self._animation:
            self._animation.stop()
        self._animation = QPropertyAnimation(self, b"value")
        self._animation.setDuration(duration)
        self._animation.setStartValue(self._value)
        self._animation.setEndValue(target_value)
        self._animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        self._animation.start()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        w = self.width()
        h = self.height()
        side = min(w, h)
        margin = self._ring_width + 20

        rect = QRectF(
            (w - side) / 2 + margin,
            (h - side) / 2 + margin,
            side - 2 * margin,
            side - 2 * margin
        )
        center = rect.center()

        # ── Ambient glow behind the ring ──
        if self._value > 0.01:
            glow_radius = rect.width() / 2 + 30
            glow_grad = QRadialGradient(center, glow_radius)
            glow_color = QColor(self._ring_color_start)
            glow_color.setAlpha(int(25 * self._value))
            glow_grad.setColorAt(0.4, glow_color)
            glow_grad.setColorAt(1.0, QColor(0, 0, 0, 0))
            painter.setBrush(QBrush(glow_grad))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawEllipse(center, glow_radius, glow_radius)

        # ── Background ring ──
        bg_pen = QPen(self._bg_ring_color, self._ring_width, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap)
        painter.setPen(bg_pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawArc(rect, 0, 360 * 16)

        # ── Inner subtle circle ──
        inner_rect = rect.adjusted(22, 22, -22, -22)
        painter.setPen(QPen(QColor(255, 255, 255, 6), 1))
        painter.drawEllipse(inner_rect)

        # ── Progress ring with gradient ──
        if self._value > 0.003:
            # Soft glow layer
            glow_color = QColor(self._ring_color_start)
            glow_color.setAlpha(35)
            glow_pen = QPen(glow_color, self._ring_width + 14, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap)
            painter.setPen(glow_pen)
            span_angle = -self._value * 360 * 16
            painter.drawArc(rect, 90 * 16, int(span_angle))

            # Main ring
            gradient = QConicalGradient(center, 90)
            gradient.setColorAt(0, self._ring_color_start)
            gradient.setColorAt(0.35, self._ring_color_end)
            gradient.setColorAt(0.7, self._ring_color_start)
            gradient.setColorAt(1, self._ring_color_start)

            progress_pen = QPen(QBrush(gradient), self._ring_width, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap)
            painter.setPen(progress_pen)
            painter.drawArc(rect, 90 * 16, int(span_angle))

        # ── Center time text ──
        painter.setPen(QColor("#FFFFFF"))
        font = QFont("Segoe UI", 40, QFont.Weight.Bold)
        font.setLetterSpacing(QFont.SpacingType.AbsoluteSpacing, 2)
        painter.setFont(font)
        time_rect = QRectF(rect.x(), rect.y() - 8, rect.width(), rect.height())
        painter.drawText(time_rect, Qt.AlignmentFlag.AlignCenter, self._text)

        # ── Sub text ──
        sub_rect = QRectF(rect.x(), rect.y() + 46, rect.width(), rect.height())
        painter.setPen(QColor(255, 255, 255, 100))
        sub_font = QFont("Segoe UI", 10, QFont.Weight.Normal)
        sub_font.setLetterSpacing(QFont.SpacingType.AbsoluteSpacing, 4)
        painter.setFont(sub_font)
        painter.drawText(sub_rect, Qt.AlignmentFlag.AlignCenter, self._sub_text)

        painter.end()
