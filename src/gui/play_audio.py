# audio_player.py
import sys, os
from PyQt6.QtCore import QUrl, Qt
from PyQt6.QtMultimedia import QMediaPlayer
from PyQt6.QtWidgets import QToolButton, QWidget, QFileDialog, QSlider, QGridLayout, QHBoxLayout, QLabel, QSizePolicy, QSpacerItem
from PyQt6.QtGui import QIcon

class AudioPlayer(QWidget):
    def __init__(self):
        super().__init__()
        
        # Initialize QMediaPlayer
        self.player = QMediaPlayer()
        
        # icon paths
        current_dir = os.path.dirname(__file__)
        play_icon_path = os.path.join(current_dir, '../assets/pictures/play.png')
        pause_icon_path = os.path.join(current_dir, '../assets/pictures/pause.png')
        stop_icon_path = os.path.join(current_dir, '../assets/pictures/stop.png')
        
        # Create tool buttons & slider
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
        
        self.current_track = QLabel(self, text="No track selected (TODO: Add track name here)")
        self.current_track.setStyleSheet("QLabel { color : #add8e6; font: bold 28px; }")

        self.current_track_layout = QHBoxLayout()
        self.current_track_layout.addWidget(self.current_track)
        
        self.volume_slider = QSlider(self)
        self.volume_slider.setOrientation(Qt.Orientation.Horizontal)
        self.volume_slider.setMaximumWidth(175)
        self.volume_slider.setMinimumWidth(75)
        self.volume_slider.setValue(50)  # Set initial volume
        
        # Connect UI actions to functions
        self.play_button.clicked.connect(self.playMusic)
        self.pause_button.clicked.connect(self.pauseMusic)
        self.stop_button.clicked.connect(self.stopMusic)
        
        self.volume_slider.valueChanged.connect(self.volumeChanged)
        
        # Set initial volume
        self.volume_slider.setValue(50)  # Example initial volume
        
        self.volume_slider_layout = QHBoxLayout()
        self.volume_slider_layout.addWidget(self.volume_slider)
        
        # Main layout
        self.main_layout = QGridLayout(self)
        self.main_layout.setColumnStretch(0, 5)
        self.main_layout.setColumnStretch(2, 2)
        self.main_layout.setColumnStretch(3, 4)
        
        # Spacer
        spacer = QSpacerItem(5, 20, QSizePolicy.Policy.Minimum)
        spacer_alt = QSpacerItem(10, 5, QSizePolicy.Policy.Minimum)
        
        # Add widgets to the layout
        self.main_layout.addLayout(self.buttons_layout, 0, 0, alignment=Qt.AlignmentFlag.AlignCenter)
        self.main_layout.addLayout(self.current_track_layout, 0, 1, alignment=Qt.AlignmentFlag.AlignCenter)
        self.main_layout.addLayout(self.volume_slider_layout, 0, 3, alignment=Qt.AlignmentFlag.AlignCenter)
        
    def playMusic(self):
        self.player.play()

    def pauseMusic(self):
        self.player.pause()

    def stopMusic(self):
        self.player.stop()

    def volumeChanged(self):
        #TODO self.player.setVolume(self.horizontalSliderVolume.value())
        print(f"Volume set to {self.volume_slider.value()}")

    def openMusicFile(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Open Music File", "", "Audio Files (*.mp3 *.wav *.flac)")
        if file_path:
            self.player.setMedia(QUrl.fromLocalFile(file_path))
            self.playMusic()

    # TODO: set a self.now_playing flag on mainwindow that updates when a new song is playing.
    def update_current_track(self, current_track):
        current_title = current_track.title
        self.current_track.setText(current_title)