"""FocusFlow - Personal Discipline & Study Optimization System.

A beautiful, modern desktop application for enforcing daily consistency,
tracking focus sessions, building streaks, and providing visual motivation.

Made by Zakir
"""
import sys
import os

# Ensure the project root is in the path
if getattr(sys, 'frozen', False):
    # Running as compiled exe
    BASE_DIR = sys._MEIPASS
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

sys.path.insert(0, BASE_DIR)

from PySide6.QtWidgets import QApplication, QSplashScreen
from PySide6.QtGui import QPixmap, QFont, QIcon, QColor, QPainter
from PySide6.QtCore import Qt, QTimer

from utils.helpers import get_resource_path


def get_logo_path():
    """Get the path to Logo.png."""
    logo = get_resource_path('Logo.png')
    if os.path.exists(logo):
        return logo
    # Fallback: check next to main.py
    return os.path.join(BASE_DIR, 'Logo.png')


def create_app_icon():
    """Load Logo.png as the application icon."""
    logo_path = get_logo_path()
    if os.path.exists(logo_path):
        return QIcon(logo_path)
    # Fallback: simple generated icon
    pixmap = QPixmap(128, 128)
    pixmap.fill(QColor(0, 0, 0, 0))
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    from PySide6.QtGui import QRadialGradient, QBrush
    gradient = QRadialGradient(64, 64, 64)
    gradient.setColorAt(0, QColor("#7B73FF"))
    gradient.setColorAt(1, QColor("#6C63FF"))
    painter.setBrush(QBrush(gradient))
    painter.setPen(Qt.PenStyle.NoPen)
    painter.drawEllipse(4, 4, 120, 120)
    painter.setPen(QColor("white"))
    painter.setFont(QFont("Segoe UI", 56, QFont.Weight.Bold))
    painter.drawText(pixmap.rect(), Qt.AlignmentFlag.AlignCenter, "F")
    painter.end()
    return QIcon(pixmap)


def create_splash():
    """Create a splash screen with Logo.png."""
    splash_pixmap = QPixmap(480, 300)
    splash_pixmap.fill(QColor("#13111C"))

    painter = QPainter(splash_pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)

    # Draw logo at top center
    logo_path = get_logo_path()
    if os.path.exists(logo_path):
        logo = QPixmap(logo_path).scaled(64, 64, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        painter.drawPixmap((480 - logo.width()) // 2, 30, logo)

    # Gradient accent line
    from PySide6.QtGui import QLinearGradient, QBrush
    grad = QLinearGradient(0, 148, 480, 148)
    grad.setColorAt(0, QColor("#6C63FF"))
    grad.setColorAt(1, QColor("#E040FB"))
    painter.setBrush(QBrush(grad))
    painter.setPen(Qt.PenStyle.NoPen)
    painter.drawRect(100, 190, 280, 3)

    # Title
    painter.setPen(QColor("white"))
    font = QFont("Segoe UI", 32, QFont.Weight.Bold)
    painter.setFont(font)
    painter.drawText(splash_pixmap.rect().adjusted(0, -40, 0, 0),
                     Qt.AlignmentFlag.AlignCenter, "FocusFlow")

    # Subtitle
    painter.setPen(QColor(255, 255, 255, 120))
    sub_font = QFont("Segoe UI", 11)
    painter.setFont(sub_font)
    painter.drawText(splash_pixmap.rect().adjusted(0, 40, 0, 0),
                     Qt.AlignmentFlag.AlignCenter, "Personal Discipline System")

    # Made by
    painter.setPen(QColor(255, 255, 255, 60))
    by_font = QFont("Segoe UI", 9)
    painter.setFont(by_font)
    painter.drawText(splash_pixmap.rect().adjusted(0, 100, 0, 0),
                     Qt.AlignmentFlag.AlignCenter, "Made by Zakir")

    painter.end()
    return QSplashScreen(splash_pixmap)


def main():
    # ── Windows taskbar icon fix ──
    # This tells Windows to treat FocusFlow as its own app (not grouped under python.exe)
    # so that Logo.png shows as the taskbar icon instead of the Python logo.
    try:
        import ctypes
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID('Zakir.FocusFlow.1.0')
    except Exception:
        pass

    # High DPI support
    os.environ['QT_ENABLE_HIGHDPI_SCALING'] = '1'

    app = QApplication(sys.argv)
    app.setApplicationName("FocusFlow")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("Zakir")

    # Set app icon from Logo.png
    icon = create_app_icon()
    app.setWindowIcon(icon)

    # Set default font
    default_font = QFont("Segoe UI", 10)
    app.setFont(default_font)

    # Show splash screen
    splash = create_splash()
    splash.show()
    app.processEvents()

    # Import and create main window (after splash is shown)
    from ui.main_window import MainWindow
    window = MainWindow()
    window.setWindowIcon(icon)  # Explicitly set on window for taskbar

    # Close splash and show window
    QTimer.singleShot(1500, lambda: (splash.close(), window.show()))

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
