"""Animation utilities for FocusFlow."""
from PySide6.QtCore import QPropertyAnimation, QEasingCurve, QSequentialAnimationGroup, QParallelAnimationGroup
from PySide6.QtWidgets import QGraphicsOpacityEffect


def fade_in(widget, duration=400):
    """Apply fade-in animation to widget."""
    effect = QGraphicsOpacityEffect(widget)
    widget.setGraphicsEffect(effect)
    animation = QPropertyAnimation(effect, b"opacity")
    animation.setDuration(duration)
    animation.setStartValue(0.0)
    animation.setEndValue(1.0)
    animation.setEasingCurve(QEasingCurve.Type.OutCubic)
    animation.start()
    widget._fade_anim = animation
    return animation


def fade_out(widget, duration=300):
    """Apply fade-out animation to widget."""
    effect = QGraphicsOpacityEffect(widget)
    widget.setGraphicsEffect(effect)
    animation = QPropertyAnimation(effect, b"opacity")
    animation.setDuration(duration)
    animation.setStartValue(1.0)
    animation.setEndValue(0.0)
    animation.setEasingCurve(QEasingCurve.Type.InCubic)
    animation.start()
    widget._fade_anim = animation
    return animation


def pulse_animation(widget, property_name=b"geometry", duration=600):
    """Create a subtle pulse effect."""
    animation = QPropertyAnimation(widget, property_name)
    animation.setDuration(duration)
    animation.setEasingCurve(QEasingCurve.Type.InOutSine)
    animation.setLoopCount(2)
    return animation


def slide_in(widget, start_offset=50, duration=400):
    """Slide widget in from below."""
    animation = QPropertyAnimation(widget, b"pos")
    animation.setDuration(duration)
    start_pos = widget.pos()
    from PySide6.QtCore import QPoint
    animation.setStartValue(QPoint(start_pos.x(), start_pos.y() + start_offset))
    animation.setEndValue(start_pos)
    animation.setEasingCurve(QEasingCurve.Type.OutCubic)
    animation.start()
    widget._slide_anim = animation
    return animation
