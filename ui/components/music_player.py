"""Music player widget for FocusFlow - inline player with playlist."""
import os
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame,
                                QPushButton, QSlider, QListWidget, QListWidgetItem,
                                QFileDialog, QAbstractItemView, QCheckBox)
from PySide6.QtCore import Qt, Slot
from PySide6.QtGui import QFont, QCursor


class MusicPlayerWidget(QWidget):
    """A compact, premium music player widget for the timer view."""

    def __init__(self, music_engine, parent=None):
        super().__init__(parent)
        self.engine = music_engine
        self._setup_ui()
        self._connect_signals()
        self._refresh_playlist()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # ── Main Card ──
        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background: rgba(255,255,255,0.025);
                border: 1px solid rgba(255,255,255,0.05);
                border-radius: 18px;
            }
        """)
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(20, 16, 20, 16)
        card_layout.setSpacing(12)

        # Header row
        header = QHBoxLayout()
        header.setSpacing(8)
        music_icon = QLabel("🎵")
        music_icon.setFont(QFont("Segoe UI Emoji", 14))
        header.addWidget(music_icon)

        title = QLabel("Focus Music")
        title.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
        title.setStyleSheet("color: white;")
        header.addWidget(title)
        header.addStretch()

        # Auto-play toggle
        self.auto_play_check = QCheckBox("Auto-play")
        self.auto_play_check.setFont(QFont("Segoe UI", 9))
        self.auto_play_check.setChecked(self.engine.auto_play_on_focus)
        self.auto_play_check.setStyleSheet("""
            QCheckBox { color: rgba(255,255,255,0.45); spacing: 6px; }
            QCheckBox::indicator {
                width: 16px; height: 16px;
                border: 2px solid rgba(255,255,255,0.15);
                border-radius: 4px;
                background: rgba(255,255,255,0.03);
            }
            QCheckBox::indicator:checked {
                background: #6C63FF;
                border-color: #6C63FF;
            }
        """)
        self.auto_play_check.toggled.connect(self.engine.set_auto_play)
        header.addWidget(self.auto_play_check)

        card_layout.addLayout(header)

        # ── Now Playing ──
        self.now_playing = QLabel("No track selected")
        self.now_playing.setFont(QFont("Segoe UI", 10))
        self.now_playing.setStyleSheet("color: rgba(255,255,255,0.5);")
        self.now_playing.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.now_playing.setWordWrap(True)
        card_layout.addWidget(self.now_playing)

        # ── Progress slider ──
        self.progress_slider = QSlider(Qt.Orientation.Horizontal)
        self.progress_slider.setRange(0, 1000)
        self.progress_slider.setValue(0)
        self.progress_slider.setFixedHeight(16)
        self.progress_slider.setStyleSheet("""
            QSlider::groove:horizontal {
                background: rgba(255,255,255,0.06);
                height: 4px;
                border-radius: 2px;
            }
            QSlider::handle:horizontal {
                background: #6C63FF;
                width: 12px;
                height: 12px;
                margin: -4px 0;
                border-radius: 6px;
            }
            QSlider::handle:horizontal:hover {
                background: #7B73FF;
                width: 14px;
                height: 14px;
                margin: -5px 0;
                border-radius: 7px;
            }
            QSlider::sub-page:horizontal {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #6C63FF, stop:1 #9D4EDD);
                border-radius: 2px;
            }
        """)
        self.progress_slider.sliderPressed.connect(self._on_slider_pressed)
        self.progress_slider.sliderReleased.connect(self._on_slider_released)
        self._slider_dragging = False
        card_layout.addWidget(self.progress_slider)

        # ── Time labels ──
        time_row = QHBoxLayout()
        self.time_current = QLabel("0:00")
        self.time_current.setFont(QFont("Segoe UI", 8))
        self.time_current.setStyleSheet("color: rgba(255,255,255,0.3);")
        self.time_total = QLabel("0:00")
        self.time_total.setFont(QFont("Segoe UI", 8))
        self.time_total.setStyleSheet("color: rgba(255,255,255,0.3);")
        time_row.addWidget(self.time_current)
        time_row.addStretch()
        time_row.addWidget(self.time_total)
        card_layout.addLayout(time_row)

        # ── Controls row ──
        controls = QHBoxLayout()
        controls.setSpacing(10)
        controls.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.shuffle_btn = self._icon_btn("🔀", 32)
        self.shuffle_btn.setToolTip("Shuffle")
        self.shuffle_btn.clicked.connect(self._toggle_shuffle)
        self._update_shuffle_style()

        self.prev_btn = self._icon_btn("⏮", 36)
        self.prev_btn.clicked.connect(self.engine.previous_track)

        self.play_btn = self._icon_btn("▶", 44)
        self.play_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #6C63FF, stop:1 #9D4EDD);
                color: white;
                border: none;
                border-radius: 22px;
                font-size: 16px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #7B73FF, stop:1 #AC5EEE);
            }
        """)
        self.play_btn.clicked.connect(self._toggle_play)

        self.next_btn = self._icon_btn("⏭", 36)
        self.next_btn.clicked.connect(self.engine.next_track)

        controls.addWidget(self.shuffle_btn)
        controls.addWidget(self.prev_btn)
        controls.addWidget(self.play_btn)
        controls.addWidget(self.next_btn)

        # Volume
        self.vol_slider = QSlider(Qt.Orientation.Horizontal)
        self.vol_slider.setRange(0, 100)
        self.vol_slider.setValue(int(self.engine.volume * 100))
        self.vol_slider.setFixedWidth(70)
        self.vol_slider.setFixedHeight(16)
        self.vol_slider.setStyleSheet("""
            QSlider::groove:horizontal {
                background: rgba(255,255,255,0.06);
                height: 3px;
                border-radius: 1px;
            }
            QSlider::handle:horizontal {
                background: rgba(255,255,255,0.5);
                width: 10px; height: 10px;
                margin: -4px 0;
                border-radius: 5px;
            }
            QSlider::sub-page:horizontal {
                background: rgba(255,255,255,0.2);
                border-radius: 1px;
            }
        """)
        self.vol_slider.valueChanged.connect(lambda v: self.engine.set_volume(v / 100.0))

        vol_icon = QLabel("🔊")
        vol_icon.setFont(QFont("Segoe UI Emoji", 9))

        controls.addSpacing(10)
        controls.addWidget(vol_icon)
        controls.addWidget(self.vol_slider)

        card_layout.addLayout(controls)

        # ── Playlist section ──
        playlist_header = QHBoxLayout()
        playlist_header.setSpacing(8)

        pl_title = QLabel("Playlist")
        pl_title.setFont(QFont("Segoe UI", 10, QFont.Weight.DemiBold))
        pl_title.setStyleSheet("color: rgba(255,255,255,0.4);")
        playlist_header.addWidget(pl_title)
        playlist_header.addStretch()

        add_btn = QPushButton("+ Add Music")
        add_btn.setFont(QFont("Segoe UI", 9, QFont.Weight.DemiBold))
        add_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        add_btn.setStyleSheet("""
            QPushButton {
                background: rgba(108,99,255,0.12);
                color: #B8B0FF;
                border: none;
                border-radius: 8px;
                padding: 5px 14px;
            }
            QPushButton:hover {
                background: rgba(108,99,255,0.2);
            }
        """)
        add_btn.clicked.connect(self._add_music)
        playlist_header.addWidget(add_btn)

        remove_btn = QPushButton("✕")
        remove_btn.setFont(QFont("Segoe UI", 10))
        remove_btn.setFixedSize(28, 28)
        remove_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        remove_btn.setToolTip("Remove selected")
        remove_btn.setStyleSheet("""
            QPushButton {
                background: rgba(255,100,100,0.1);
                color: rgba(255,100,100,0.6);
                border: none;
                border-radius: 8px;
            }
            QPushButton:hover {
                background: rgba(255,100,100,0.2);
                color: #FF6B6B;
            }
        """)
        remove_btn.clicked.connect(self._remove_selected)
        playlist_header.addWidget(remove_btn)

        card_layout.addLayout(playlist_header)

        # Playlist list
        self.playlist_widget = QListWidget()
        self.playlist_widget.setMaximumHeight(140)
        self.playlist_widget.setFont(QFont("Segoe UI", 10))
        self.playlist_widget.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.playlist_widget.setStyleSheet("""
            QListWidget {
                background: rgba(255,255,255,0.02);
                border: 1px solid rgba(255,255,255,0.04);
                border-radius: 12px;
                padding: 6px;
                outline: none;
            }
            QListWidget::item {
                color: rgba(255,255,255,0.6);
                padding: 7px 12px;
                border-radius: 8px;
                margin: 1px 0;
            }
            QListWidget::item:hover {
                background: rgba(255,255,255,0.04);
                color: rgba(255,255,255,0.8);
            }
            QListWidget::item:selected {
                background: rgba(108,99,255,0.15);
                color: #B8B0FF;
            }
        """)
        self.playlist_widget.doubleClicked.connect(self._on_track_double_click)
        card_layout.addWidget(self.playlist_widget)

        layout.addWidget(card)

    def _icon_btn(self, text, size):
        btn = QPushButton(text)
        btn.setFixedSize(size, size)
        btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        btn.setStyleSheet("""
            QPushButton {
                background: rgba(255,255,255,0.05);
                color: rgba(255,255,255,0.6);
                border: none;
                border-radius: """ + str(size // 2) + """px;
                font-size: 13px;
            }
            QPushButton:hover {
                background: rgba(255,255,255,0.1);
                color: white;
            }
        """)
        return btn

    def _connect_signals(self):
        self.engine.track_changed.connect(self._on_track_changed)
        self.engine.playback_state_changed.connect(self._on_state_changed)
        self.engine.playlist_updated.connect(self._refresh_playlist)
        self.engine.position_changed.connect(self._on_position)

    @Slot(str)
    def _on_track_changed(self, name):
        self.now_playing.setText(f"♪  {name}")
        self.now_playing.setStyleSheet("color: #B8B0FF;")
        # Highlight in playlist
        for i in range(self.playlist_widget.count()):
            item = self.playlist_widget.item(i)
            if item.text().lstrip("▶ ♪ ") == name or item.text() == name:
                self.playlist_widget.setCurrentItem(item)
                break

    @Slot(str)
    def _on_state_changed(self, state):
        if state == 'playing':
            self.play_btn.setText("⏸")
        else:
            self.play_btn.setText("▶")

    @Slot(int, int)
    def _on_position(self, current_ms, total_ms):
        if not self._slider_dragging and total_ms > 0:
            self.progress_slider.setValue(int(current_ms / total_ms * 1000))
        self.time_current.setText(self._format_ms(current_ms))
        self.time_total.setText(self._format_ms(total_ms))

    def _format_ms(self, ms):
        secs = ms // 1000
        m = secs // 60
        s = secs % 60
        return f"{m}:{s:02d}"

    def _toggle_play(self):
        self.engine.toggle_play_pause()

    def _toggle_shuffle(self):
        self.engine.set_shuffle(not self.engine.shuffle_mode)
        self._update_shuffle_style()

    def _update_shuffle_style(self):
        if self.engine.shuffle_mode:
            self.shuffle_btn.setStyleSheet("""
                QPushButton {
                    background: rgba(108,99,255,0.2);
                    color: #B8B0FF;
                    border: none;
                    border-radius: 16px;
                    font-size: 13px;
                }
                QPushButton:hover { background: rgba(108,99,255,0.3); }
            """)
        else:
            self.shuffle_btn.setStyleSheet("""
                QPushButton {
                    background: rgba(255,255,255,0.05);
                    color: rgba(255,255,255,0.4);
                    border: none;
                    border-radius: 16px;
                    font-size: 13px;
                }
                QPushButton:hover {
                    background: rgba(255,255,255,0.1);
                    color: rgba(255,255,255,0.7);
                }
            """)

    def _add_music(self):
        files, _ = QFileDialog.getOpenFileNames(
            self, "Add Music Files", "",
            "Audio Files (*.mp3 *.wav *.ogg *.flac *.m4a *.wma *.aac);;All Files (*)"
        )
        if files:
            self.engine.add_files(files)

    def _remove_selected(self):
        current = self.playlist_widget.currentRow()
        if current >= 0:
            self.engine.remove_track(current)

    def _on_track_double_click(self, index):
        self.engine.play(index.row())

    def _on_slider_pressed(self):
        self._slider_dragging = True

    def _on_slider_released(self):
        self._slider_dragging = False
        if self.engine._duration > 0:
            pos = int(self.progress_slider.value() / 1000 * self.engine._duration)
            self.engine.set_position(pos)

    @Slot(list)
    def _refresh_playlist(self, tracks=None):
        if tracks is None:
            tracks = self.engine.playlist
        self.playlist_widget.clear()
        for name in tracks:
            item = QListWidgetItem(f"  {name}")
            self.playlist_widget.addItem(item)
        if not tracks:
            self.now_playing.setText("No tracks — click '+ Add Music'")
            self.now_playing.setStyleSheet("color: rgba(255,255,255,0.35);")
