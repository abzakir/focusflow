"""Timer view for FocusFlow - premium timer page with music player."""
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                                QFrame, QScrollArea, QSplitter)
from PySide6.QtCore import Qt, Slot
from PySide6.QtGui import QFont

from ui.components.circular_progress import CircularProgress
from ui.components.custom_button import CustomButton
from ui.components.music_player import MusicPlayerWidget
from utils.helpers import format_time


class TimerView(QWidget):
    """Focus timer view with circular progress ring, controls, and music player."""

    def __init__(self, timer_engine, music_engine=None, parent=None):
        super().__init__(parent)
        self.timer_engine = timer_engine
        self.music_engine = music_engine
        self._setup_ui()
        self._connect_signals()
        self._update_display(self.timer_engine.remaining)

    def _setup_ui(self):
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # ── Left: Timer area ──
        timer_widget = QWidget()
        timer_layout = QVBoxLayout(timer_widget)
        timer_layout.setContentsMargins(40, 40, 20, 40)
        timer_layout.setSpacing(0)
        timer_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Mode indicator
        self.mode_label = QLabel("FOCUS SESSION")
        self.mode_label.setFont(QFont("Segoe UI", 11))
        self.mode_label.setStyleSheet(
            "color: rgba(255,255,255,0.35); letter-spacing: 5px; font-weight: 600;"
        )
        self.mode_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        timer_layout.addWidget(self.mode_label)
        timer_layout.addSpacing(25)

        # Circular progress ring
        self.progress_ring = CircularProgress()
        self.progress_ring.setFixedSize(320, 320)
        ring_container = QHBoxLayout()
        ring_container.setAlignment(Qt.AlignmentFlag.AlignCenter)
        ring_container.addWidget(self.progress_ring)
        timer_layout.addLayout(ring_container)
        timer_layout.addSpacing(35)

        # Control buttons
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(14)
        btn_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.start_btn = CustomButton("▶  Start", variant="primary")
        self.start_btn.setFixedSize(150, 48)
        self.start_btn.clicked.connect(self._on_start)

        self.pause_btn = CustomButton("⏸  Pause", variant="secondary")
        self.pause_btn.setFixedSize(150, 48)
        self.pause_btn.clicked.connect(self._on_pause)
        self.pause_btn.setVisible(False)

        self.reset_btn = CustomButton("↺  Reset", variant="secondary")
        self.reset_btn.setFixedSize(130, 48)
        self.reset_btn.clicked.connect(self._on_reset)

        self.skip_btn = CustomButton("⏭  Skip", variant="secondary")
        self.skip_btn.setFixedSize(110, 48)
        self.skip_btn.clicked.connect(self._on_skip)

        btn_layout.addWidget(self.start_btn)
        btn_layout.addWidget(self.pause_btn)
        btn_layout.addWidget(self.reset_btn)
        btn_layout.addWidget(self.skip_btn)
        timer_layout.addLayout(btn_layout)
        timer_layout.addSpacing(28)

        # Mode toggle
        toggle_frame = QFrame()
        toggle_frame.setStyleSheet("""
            QFrame {
                background: rgba(255,255,255,0.03);
                border: 1px solid rgba(255,255,255,0.06);
                border-radius: 14px;
            }
        """)
        toggle_frame.setFixedHeight(50)
        toggle_layout = QHBoxLayout(toggle_frame)
        toggle_layout.setContentsMargins(6, 4, 6, 4)
        toggle_layout.setSpacing(6)

        self.focus_mode_btn = CustomButton("🎯 Focus", variant="primary")
        self.focus_mode_btn.setFixedHeight(38)
        self.focus_mode_btn.clicked.connect(lambda: self._set_mode('focus'))

        self.break_mode_btn = CustomButton("☕ Break", variant="secondary")
        self.break_mode_btn.setFixedHeight(38)
        self.break_mode_btn.clicked.connect(lambda: self._set_mode('break'))

        toggle_layout.addWidget(self.focus_mode_btn)
        toggle_layout.addWidget(self.break_mode_btn)

        mode_container = QHBoxLayout()
        mode_container.setAlignment(Qt.AlignmentFlag.AlignCenter)
        toggle_frame.setFixedWidth(260)
        mode_container.addWidget(toggle_frame)
        timer_layout.addLayout(mode_container)
        timer_layout.addSpacing(20)

        # Status text
        self.status_label = QLabel("Ready to focus")
        self.status_label.setFont(QFont("Segoe UI", 10))
        self.status_label.setStyleSheet("color: rgba(255,255,255,0.3);")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        timer_layout.addWidget(self.status_label)
        timer_layout.addStretch()

        main_layout.addWidget(timer_widget, stretch=3)

        # ── Right: Music Player Panel ──
        if self.music_engine:
            music_panel = QWidget()
            music_panel_layout = QVBoxLayout(music_panel)
            music_panel_layout.setContentsMargins(10, 30, 30, 30)
            music_panel_layout.setSpacing(0)

            self.music_player = MusicPlayerWidget(self.music_engine)
            music_panel_layout.addWidget(self.music_player)
            music_panel_layout.addStretch()

            main_layout.addWidget(music_panel, stretch=2)

    def _connect_signals(self):
        self.timer_engine.tick.connect(self._update_display)
        self.timer_engine.state_changed.connect(self._on_state_changed)
        self.timer_engine.mode_changed.connect(self._on_mode_changed)
        self.timer_engine.session_completed.connect(self._on_session_completed)

    @Slot(int)
    def _update_display(self, remaining):
        self.progress_ring.set_text(format_time(remaining))
        self.progress_ring.set_value(self.timer_engine.progress)

    @Slot(str)
    def _on_state_changed(self, state):
        if state == 'running':
            self.start_btn.setVisible(False)
            self.pause_btn.setVisible(True)
            self.status_label.setText("Session in progress...")
            self.status_label.setStyleSheet("color: rgba(108,99,255,0.6);")
            self.focus_mode_btn.setEnabled(False)
            self.break_mode_btn.setEnabled(False)
        elif state == 'paused':
            self.start_btn.setVisible(True)
            self.pause_btn.setVisible(False)
            self.start_btn.setText("▶  Resume")
            self.status_label.setText("⏸ Paused")
            self.status_label.setStyleSheet("color: rgba(255,217,61,0.6);")
            self.focus_mode_btn.setEnabled(False)
            self.break_mode_btn.setEnabled(False)
        else:
            self.start_btn.setVisible(True)
            self.pause_btn.setVisible(False)
            self.start_btn.setText("▶  Start")
            self.status_label.setText("Ready to focus")
            self.status_label.setStyleSheet("color: rgba(255,255,255,0.3);")
            self.focus_mode_btn.setEnabled(True)
            self.break_mode_btn.setEnabled(True)

    @Slot(str)
    def _on_mode_changed(self, mode):
        if mode == 'focus':
            self.mode_label.setText("FOCUS SESSION")
            self.progress_ring.set_sub_text("FOCUS")
            self.progress_ring.set_colors("#6C63FF", "#E040FB")
            self.focus_mode_btn.set_variant("primary")
            self.break_mode_btn.set_variant("secondary")
        else:
            self.mode_label.setText("BREAK TIME")
            self.progress_ring.set_sub_text("BREAK")
            self.progress_ring.set_colors("#00C9A7", "#00D4FF")
            self.focus_mode_btn.set_variant("secondary")
            self.break_mode_btn.set_variant("primary")

    @Slot(str, float)
    def _on_session_completed(self, session_type, duration):
        if session_type == 'focus':
            self.status_label.setText(f"✅ Focus complete! ({duration:.0f} min)")
            self.status_label.setStyleSheet("color: #6BCB77;")
        else:
            self.status_label.setText("Break over — time to focus!")
            self.status_label.setStyleSheet("color: rgba(255,255,255,0.3);")

    def _on_start(self):
        self.timer_engine.start()

    def _on_pause(self):
        self.timer_engine.pause()

    def _on_reset(self):
        self.timer_engine.reset()
        self.status_label.setStyleSheet("color: rgba(255,255,255,0.3);")

    def _on_skip(self):
        self.timer_engine.skip()

    def _set_mode(self, mode):
        self.timer_engine.set_mode(mode)

    def refresh(self):
        self._update_display(self.timer_engine.remaining)
