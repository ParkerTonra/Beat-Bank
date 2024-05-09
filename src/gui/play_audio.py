import sys
import os
from time import sleep
from PyQt6.QtCore import QUrl, Qt, QThread, pyqtSignal, QTimer
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput
from PyQt6.QtWidgets import QToolButton, QWidget, QFileDialog, QSlider, QGridLayout, QHBoxLayout, QLabel, QSizePolicy, QSpacerItem
from PyQt6.QtGui import QIcon
from src.gui.signals import PlayAudioSignal
import logging
from threading import Lock

logger = logging.getLogger(__name__)


class AudioPlayer(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.init_audio_player()

        self.init_icons()
        self.init_buttons()
        self.init_labels()
        self.init_volume_slider()
        self.init_position_slider()
        self.layouts_add_widgets()

    def init_audio_player(self):
        self.player = QMediaPlayer(self)
        self.audio_out = QAudioOutput(self)
        self.player.setAudioOutput(self.audio_out)

        self.player.positionChanged.connect(self.positionChanged)
        self.player.durationChanged.connect(self.durationChanged)

        self.player.errorOccurred.connect(self.handleError)

        self.player.mediaStatusChanged.connect(self.mediaStatusChanged)

    def layouts_add_widgets(self):
        self.main_layout = QGridLayout(self)
        self.main_layout.addLayout(self.buttons_layout, 0, 0)
        self.main_layout.addWidget(self.current_track_label, 0, 1)
        self.main_layout.addWidget(self.volume_slider, 0, 2)

        # Adding to main layout
        self.main_layout.addLayout(self.time_layout, 1, 0, 1, 1)

        # Span across 2 columns
        self.main_layout.addWidget(self.position_slider, 1, 1, 1, 2)

        # Set the stretch factors
        self.main_layout.setColumnStretch(0, 1)
        self.main_layout.setColumnStretch(1, 3)
        self.main_layout.setColumnStretch(2, 1)

    def init_icons(self):
        current_dir = os.path.dirname(__file__)
        self.play_icon = QIcon(os.path.join(
            current_dir, '../assets/pictures/play.png'))
        self.pause_icon = QIcon(os.path.join(
            current_dir, '../assets/pictures/pause.png'))
        self.stop_icon = QIcon(os.path.join(
            current_dir, '../assets/pictures/stop.png'))

    def init_buttons(self):
        self.init_play_pause_button()
        self.init_stop_button()  # Not currently used
        self.buttons_layout = QHBoxLayout()
        self.buttons_layout.addWidget(self.play_pause_button)
        self.buttons_layout.addWidget(self.stop_button)

    def init_labels(self):
        self.init_current_track_label()
        self.init_time_labels()

    def init_time_labels(self):
        self.current_time_label = QLabel("00:00", self)
        self.total_duration_label = QLabel("00:00", self)

        self.time_layout = QHBoxLayout()
        self.time_layout.addWidget(self.current_time_label)
        self.time_layout.addWidget(
            self.total_duration_label, alignment=Qt.AlignmentFlag.AlignRight)

    def init_play_pause_button(self):
        self.play_pause_button = QToolButton(self)
        self.play_pause_button.setIcon(self.play_icon)
        self.play_pause_button.setIconSize(self.play_pause_button.sizeHint())
        self.play_pause_button.clicked.connect(self.play_or_pause)

    def init_stop_button(self):
        self.stop_button = QToolButton(self)
        self.stop_button.setIcon(self.stop_icon)
        self.stop_button.setIconSize(self.stop_button.sizeHint())
        self.stop_button.clicked.connect(self.stopMusic)

    def init_current_track_label(self):
        self.current_track_label = QLabel(self, text="No track selected")
        self.current_track_label.setStyleSheet(
            "QLabel { color : #add8e6; font: bold 22px; text-align: center; }")
        self.current_track_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

    def init_volume_slider(self):
        self.volume_slider = QSlider(self)
        self.volume_slider.setOrientation(Qt.Orientation.Horizontal)
        self.volume_slider.setMaximumWidth(175)
        self.volume_slider.setMinimumWidth(75)
        self.volume_slider.setValue(100)
        self.volume_slider.valueChanged.connect(self.volumeChanged)

    def init_position_slider(self):
        self.position_slider = QSlider(Qt.Orientation.Horizontal)
        self.position_slider.setRange(0, 100)
        self.position_slider.sliderMoved.connect(self.setPosition)

    def positionChanged(self, position):
        self.position_slider.setValue(position)
        self.update_time_label(position, self.current_time_label)

    def durationChanged(self, duration):
        self.position_slider.setRange(0, duration)
        self.update_time_label(
            self.position_slider.value(), self.current_time_label)

    def setPosition(self, position):
        self.player.setPosition(position)
        self.update_time_label(
            self.position_slider.value(), self.current_time_label)

    def update_time_label(self, milliseconds, label):
        """Helper function to convert milliseconds to a mm:ss format and update the label."""
        seconds = int(milliseconds / 1000)
        minutes = seconds // 60
        seconds = seconds % 60
        label.setText(f"{minutes:02}:{seconds:02}")

    def playAudio(self, audio_path=None, audio_length=None):
        logger.info("playAudio function called.")
        try:
            if not audio_path:
                logger.info("No file selected.")
                return
            logger.info(
                f"Attempting to play: {audio_path}, length: {audio_length}")
            url = QUrl.fromLocalFile(audio_path)
            self.player.setSource(url)
            self.player.play()
            self.update_ui_isPlaying()

            self.current_track_label.setText(os.path.basename(audio_path))
            self.total_duration_label.setText(audio_length)

        except Exception as e:
            logger.info(f"Failed to play audio: {e}")

    def play_or_pause(self):
        logger.info("play/pause button pressed")
        if self.player.isPlaying():
            self.pause_music()
        else:
            if self.player.hasAudio():
                self.resume_music()
            else:
                logger.info("No audio loaded")

    def resume_music(self):
        self.player.play()
        self.update_ui_isPlaying()

    def update_ui_isPlaying(self):
        self.play_pause_button.setIcon(self.pause_icon)

    def update_ui_isPaused(self):
        self.play_pause_button.setIcon(self.play_icon)

    def pause_music(self):
        try:
            self.player.pause()
            self.update_ui_isPaused()
        except Exception as e:
            logger.info(f"Failed to pause audio: {e}")

    def stopMusic(self):
        try:
            self.player.stop()
            self.update_ui_isPaused()  # Ensure UI updates correctly to reflect the stopped state
        except Exception as e:
            logger.info(f"Failed to stop audio: {e}")

    def volumeChanged(self):
        try:
            self.audio_out.setVolume(self.volume_slider.value() / 100)
        except Exception as e:
            logger.info(f"Failed to set volume: {e}")

    def handleError(self, error, errorString):
        logger.info(f"Error occurred: {errorString}, Error Type: {error}")

    def mediaStatusChanged(self, status):
        if status == QMediaPlayer.MediaStatus.LoadedMedia:
            logger.info("Media loaded successfully")
        elif status == QMediaPlayer.MediaStatus.EndOfMedia:
            logger.info("Playback finished")
        elif status == QMediaPlayer.MediaStatus.InvalidMedia:
            logger.info("Invalid media")
        elif status == QMediaPlayer.MediaStatus.NoMedia:
            logger.info("No media loaded")
        elif status == QMediaPlayer.MediaStatus.BufferingMedia:
            logger.info("Buffering media")
        elif status == QMediaPlayer.MediaStatus.BufferingMedia:
            logger.info("Buffering: " +
                        str(self.player.bufferProgress()) + "%")
        # Add more cases as needed based on your application's requirements

    def errorOccurred(self, error, errorString):
        logger.info(f"Error occurred: {errorString}, Error Type: {error}")
        # Optionally, you can add logic to retry loading the media or to skip to next media


class Node:
    def __init__(self, beat_path, beat_length, prev=None, next=None):
        self.beat_path = beat_path
        self.beat_length = beat_length
        self.prev = None
        self.next = None


class BeatJockey:
    def __init__(self, main_window, audio_player):
        self.main_window = main_window
        self.audio_player = audio_player
        logger.info(f"audio player at beat jockey: {self.audio_player}")
        self.current = Node("dummy_path", "00:00")  # Dummy node initialization

    def update_current_song(self, path, length):
        logger.info(f"update_current_song called")
        if self.current:
            self.current.beat_path = path
            self.current.beat_length = length
        else:
            logger.info("No current song to update.")
            self.add_song(path, length)

    def add_song(self, beat_path, beat_length):
        logger.info(f"add_song called")
        new_node = Node(beat_path, beat_length)
        if not self.current:
            self.current = new_node
            self.current.prev = self.current
            self.current.next = self.current
        else:
            last = self.current.prev
            last.next = new_node
            new_node.prev = last
            new_node.next = self.current
            self.current.prev = new_node
            self.current = new_node

    def play_song_by_path(self, path, length):
        logger.info(f"play_song_by_path called")

        self.audio_player.playAudio(path, length)

    def play_current_song(self):
        logger.info("play_current_song called")
        self.play_song_by_path(self.current.beat_path,
                               self.current.beat_length)

    def on_playback_interrupted(self):
        logger.info("on_playback_interrupted called")
        logger.info("Playback interrupted.")
        # Here, you could also set up the next song or handle other cleanup

    def on_playback_finished(self, success):
        logger.info("on_playback_finished called")
        if success:
            logger.info("Playback finished successfully.")
        else:
            logger.info("Playback ended with errors.")
            # log the error
        self.cleanup_after_playback()

    def cleanup_after_playback(self):
        logger.info("Cleaning up after playback")
        # Example cleanup logic
        self.audio_player.stopMusic()  # Stop the audio player
        self.audio_player.current_track_label.setText("No track Playing")
        self.audio_player.total_duration_label.setText("00:00")

    def play_next_song(self):
        logger.info("play_next_song called")
        if self.current:
            self.current = self.current.next
            self.play_current_song()

    def play_previous_song(self):
        logger.info("play_previous_song called")
        if self.current:
            self.current = self.current.prev
            self.play_current_song()

    def get_current_song(self):
        pass

    def get_current_path(self, current):
        pass
