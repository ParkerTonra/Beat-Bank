import sys
from src.models.track import Track
from src.gui.edit_track_window import EditTrackWindow
from PyQt5.QtWidgets import QApplication



track = Track(title='Test Track', artist='Test Artist', length='3:00', file_path='test_path', BPM=120)
app = QApplication(sys.argv)
edit_window = EditTrackWindow()
edit_window.setTrackInfo(track)
sys.exit(app.exec_())