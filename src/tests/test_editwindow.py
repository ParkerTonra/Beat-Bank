import sys
from src.models.track import Track
from src.gui.edit_track_window import EditTrackWindow
from PyQt6.QtWidgets import QApplication



track = Track(title='Test Track', artist='Test Artist', length='3:00', BPM='120')
app = QApplication(sys.argv)
edit_window = EditTrackWindow()
edit_window.setTrackInfo(track)
edit_window.show()
sys.exit(app.exec())