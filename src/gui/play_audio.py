import sys, os
from PyQt6.QtCore import QUrl, Qt
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput
from PyQt6.QtWidgets import QToolButton, QWidget, QFileDialog, QSlider, QGridLayout, QHBoxLayout, QLabel, QSizePolicy, QSpacerItem
from PyQt6.QtGui import QIcon
from gui.signals import PlayAudioSignal

class AudioPlayer(QWidget):
    def __init__(self, main_window, beat_jockey):
        super().__init__()
        self.player = QMediaPlayer()
        self.audio_out = QAudioOutput()
        self.player.setAudioOutput(self.audio_out)
        self.player.positionChanged.connect(self.positionChanged)
        self.player.errorOccurred.connect(self.handleError)
        self.main_window = main_window
        self.beat_jockey = beat_jockey

        current_dir = os.path.dirname(__file__)
        play_icon_path = os.path.join(current_dir, '../assets/pictures/play.png')
        pause_icon_path = os.path.join(current_dir, '../assets/pictures/pause.png')
        stop_icon_path = os.path.join(current_dir, '../assets/pictures/stop.png')

        self.play_button = QToolButton(self)
        self.play_button.setIcon(QIcon(play_icon_path))
        self.play_button.setIconSize(self.play_button.sizeHint())

        self.pause_button = QToolButton(self)
        self.pause_button.setIcon(QIcon(pause_icon_path))
        self.pause_button.setIconSize(self.pause_button.sizeHint())

        self.stop_button = QToolButton(self)
        self.stop_button.setIcon(QIcon(stop_icon_path))
        self.stop_button.setIconSize(self.stop_button.sizeHint())

        self.buttons_layout = QHBoxLayout()
        self.buttons_layout.addWidget(self.play_button)
        self.buttons_layout.addWidget(self.pause_button)
        self.buttons_layout.addWidget(self.stop_button)

        self.current_track = QLabel(self, text="No track selected")
        self.current_track.setStyleSheet("QLabel { color : #add8e6; font: bold 28px; }")

        self.volume_slider = QSlider(self)
        self.volume_slider.setOrientation(Qt.Orientation.Horizontal)
        self.volume_slider.setMaximumWidth(175)
        self.volume_slider.setMinimumWidth(75)
        self.volume_slider.setValue(50)

        self.play_button.clicked.connect(self.playAudio)
        self.pause_button.clicked.connect(self.pauseMusic)
        self.stop_button.clicked.connect(self.stopMusic)
        self.volume_slider.valueChanged.connect(self.volumeChanged)

        self.main_layout = QGridLayout(self)
        self.main_layout.addLayout(self.buttons_layout, 0, 0)
        self.main_layout.addWidget(self.current_track, 0, 1)
        self.main_layout.addWidget(self.volume_slider, 0, 2)

    def playAudio(self, audio_path=None):
        try:
            file_path = audio_path.current.song_data
            print(f"!!!!!! {file_path}")
            if file_path:
                print(file_path)
                self.player.setSource(QUrl.fromLocalFile(file_path))
                self.player.play()
                self.current_track.setText(os.path.basename(file_path))
            else:
                print("No file selected.")
        except Exception as e:
            print(f"Failed to play audio: {e}")

    def pauseMusic(self):
        try:
            self.player.pause()
        except Exception as e:
            print(f"Failed to pause audio: {e}")

    def stopMusic(self):
        try:
            self.player.stop()
        except Exception as e:
            print(f"Failed to stop audio: {e}")

    def volumeChanged(self):
        try:
            self.player.setVolume(self.volume_slider.value())
        except Exception as e:
            print(f"Failed to set volume: {e}")

    def positionChanged(self, position):
        pass

    def handleError(self, error, errorString):
        print(f"Error occurred: {errorString}")

class Node:
    def __init__(self, song_data, prev=None, next=None):
        self.song_data = song_data
        self.prev = prev
        self.next = next

class BeatJockey:
    def __init__(self, main_window):
        self.current = None
        self.main_window = main_window
    def add_song(self, song_data):
        new_node = Node(song_data)
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

    def play_current_song(self):
        if self.current:
            print("Playing current song:", self.current.song_data)
            # Implement code to play the current song
    
    def play_next_song(self):
        if self.current:
            self.current = self.current.next
            self.play_current_song()
            
    def play_previous_song(self):
        if self.current:
            self.current = self.current.prev
            self.play_current_song()

    def get_current_song(self):
        pass
    
    def get_current_path(self, current):
        pass
    
    def update_current_song(self, path):
        print(f"updating current song (path) to {path}")
        if self.current:
            self.current.song_data = path
        else:
            # If no current node exists, create one
            self.current = Node(path)
            self.current.prev = self.current
            self.current.next = self.current
