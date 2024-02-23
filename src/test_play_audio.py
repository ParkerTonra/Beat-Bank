import sys
from gui.play_audio import AudioPlayer
from models.track import Track
from PyQt6.QtWidgets import QApplication


track = Track(title='Test Track', artist='Test Artist', length='3:00', bpm='120')
app = QApplication(sys.argv)
audio_player = AudioPlayer()
audio_player.show()
sys.exit(app.exec())

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    window = AudioPlayer()
    window.show()  # Show the audio player widget
    
    sys.exit(app.exec())