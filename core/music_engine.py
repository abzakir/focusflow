"""Music engine for FocusFlow - manages audio playback during focus sessions."""
import os
import random
from PySide6.QtCore import QObject, Signal, QUrl, Slot
from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput


class MusicEngine(QObject):
    """Manages music playback with queue, sequential/shuffle modes."""

    # Signals
    track_changed = Signal(str)        # track name
    playback_state_changed = Signal(str)  # 'playing', 'paused', 'stopped'
    playlist_updated = Signal(list)    # list of track names
    position_changed = Signal(int, int)  # current_ms, total_ms

    def __init__(self, db_manager, parent=None):
        super().__init__(parent)
        self.db = db_manager

        # Player setup
        self._player = QMediaPlayer(self)
        self._audio_output = QAudioOutput(self)
        self._player.setAudioOutput(self._audio_output)

        # State
        self._playlist = []        # list of full file paths
        self._current_index = -1
        self._shuffle = False
        self._shuffle_order = []
        self._auto_play_on_focus = False  # user preference
        self._is_playing = False

        # Volume (0.0 - 1.0)
        volume = float(self.db.get_setting('music_volume', '0.5'))
        self._audio_output.setVolume(volume)

        # Load preferences
        self._shuffle = self.db.get_setting('music_shuffle', 'false') == 'true'
        self._auto_play_on_focus = self.db.get_setting('music_auto_play', 'true') == 'true'

        # Load saved playlist
        self._load_saved_playlist()

        # Connections
        self._player.mediaStatusChanged.connect(self._on_media_status)
        self._player.positionChanged.connect(self._on_position_changed)
        self._player.durationChanged.connect(self._on_duration_changed)

        self._duration = 0

    @property
    def is_playing(self):
        return self._player.playbackState() == QMediaPlayer.PlaybackState.PlayingState

    @property
    def current_track_name(self):
        if 0 <= self._current_index < len(self._playlist):
            return os.path.splitext(os.path.basename(self._playlist[self._current_index]))[0]
        return ""

    @property
    def playlist(self):
        return [os.path.splitext(os.path.basename(p))[0] for p in self._playlist]

    @property
    def shuffle_mode(self):
        return self._shuffle

    @property
    def auto_play_on_focus(self):
        return self._auto_play_on_focus

    @property
    def volume(self):
        return self._audio_output.volume()

    def add_files(self, file_paths):
        """Add music files to the playlist."""
        valid_extensions = {'.mp3', '.wav', '.ogg', '.flac', '.m4a', '.wma', '.aac'}
        added = []
        for path in file_paths:
            ext = os.path.splitext(path)[1].lower()
            if ext in valid_extensions and path not in self._playlist:
                self._playlist.append(path)
                added.append(path)

        if added:
            self._save_playlist()
            self._rebuild_shuffle_order()
            self.playlist_updated.emit(self.playlist)

    def remove_track(self, index):
        """Remove a track from the playlist by index."""
        if 0 <= index < len(self._playlist):
            was_playing = (index == self._current_index and self.is_playing)
            self._playlist.pop(index)

            if was_playing:
                self.stop()
            elif self._current_index > index:
                self._current_index -= 1
            elif self._current_index == index:
                self._current_index = min(self._current_index, len(self._playlist) - 1)

            self._save_playlist()
            self._rebuild_shuffle_order()
            self.playlist_updated.emit(self.playlist)

    def clear_playlist(self):
        """Clear all tracks."""
        self.stop()
        self._playlist.clear()
        self._current_index = -1
        self._save_playlist()
        self.playlist_updated.emit(self.playlist)

    def play(self, index=None):
        """Start playing. Optionally jump to a specific track index."""
        if not self._playlist:
            return

        if index is not None and 0 <= index < len(self._playlist):
            self._current_index = index
        elif self._current_index < 0:
            self._current_index = 0

        self._load_and_play(self._current_index)

    def pause(self):
        """Pause playback."""
        if self.is_playing:
            self._player.pause()
            self.playback_state_changed.emit('paused')

    def resume(self):
        """Resume paused playback."""
        if self._player.playbackState() == QMediaPlayer.PlaybackState.PausedState:
            self._player.play()
            self.playback_state_changed.emit('playing')

    def toggle_play_pause(self):
        """Toggle between play and pause."""
        if self.is_playing:
            self.pause()
        elif self._player.playbackState() == QMediaPlayer.PlaybackState.PausedState:
            self.resume()
        else:
            self.play()

    def stop(self):
        """Stop playback."""
        self._player.stop()
        self.playback_state_changed.emit('stopped')

    def next_track(self):
        """Skip to next track."""
        if not self._playlist:
            return
        if self._shuffle:
            self._current_index = self._next_shuffle_index()
        else:
            self._current_index = (self._current_index + 1) % len(self._playlist)
        self._load_and_play(self._current_index)

    def previous_track(self):
        """Go to previous track."""
        if not self._playlist:
            return
        self._current_index = (self._current_index - 1) % len(self._playlist)
        self._load_and_play(self._current_index)

    def set_volume(self, value):
        """Set volume (0.0 - 1.0)."""
        self._audio_output.setVolume(value)
        self.db.set_setting('music_volume', str(round(value, 2)))

    def set_shuffle(self, enabled):
        """Enable or disable shuffle mode."""
        self._shuffle = enabled
        self.db.set_setting('music_shuffle', 'true' if enabled else 'false')
        if enabled:
            self._rebuild_shuffle_order()

    def set_auto_play(self, enabled):
        """Set whether music auto-plays when focus session starts."""
        self._auto_play_on_focus = enabled
        self.db.set_setting('music_auto_play', 'true' if enabled else 'false')

    def on_focus_started(self):
        """Called when a focus session starts."""
        if self._auto_play_on_focus and self._playlist:
            self.play()

    def on_focus_ended(self):
        """Called when a focus session ends (or break starts)."""
        if self.is_playing:
            self.pause()

    def set_position(self, ms):
        """Seek to position in milliseconds."""
        self._player.setPosition(ms)

    # ── Private methods ──

    def _load_and_play(self, index):
        if 0 <= index < len(self._playlist):
            path = self._playlist[index]
            if os.path.exists(path):
                self._player.setSource(QUrl.fromLocalFile(path))
                self._player.play()
                self.track_changed.emit(self.current_track_name)
                self.playback_state_changed.emit('playing')
            else:
                # File removed — skip to next
                self._playlist.pop(index)
                self._save_playlist()
                if self._playlist:
                    self.next_track()

    def _on_media_status(self, status):
        if status == QMediaPlayer.MediaStatus.EndOfMedia:
            self.next_track()

    def _on_position_changed(self, position):
        self.position_changed.emit(position, self._duration)

    def _on_duration_changed(self, duration):
        self._duration = duration

    def _rebuild_shuffle_order(self):
        self._shuffle_order = list(range(len(self._playlist)))
        random.shuffle(self._shuffle_order)
        self._shuffle_pos = 0

    def _next_shuffle_index(self):
        if not self._shuffle_order:
            self._rebuild_shuffle_order()
        self._shuffle_pos = (getattr(self, '_shuffle_pos', 0) + 1) % len(self._shuffle_order)
        if self._shuffle_pos == 0:
            self._rebuild_shuffle_order()
        return self._shuffle_order[self._shuffle_pos]

    def _save_playlist(self):
        """Save playlist paths to database."""
        data = '|'.join(self._playlist)
        self.db.set_setting('music_playlist', data)

    def _load_saved_playlist(self):
        """Load saved playlist from database."""
        data = self.db.get_setting('music_playlist', '')
        if data:
            paths = data.split('|')
            self._playlist = [p for p in paths if os.path.exists(p)]
            self._rebuild_shuffle_order()
