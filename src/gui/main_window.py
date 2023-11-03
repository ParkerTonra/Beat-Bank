import sys
import os
import threading
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QTableWidget, QTableWidgetItem,
    QPushButton, QVBoxLayout, QWidget, QLabel, QFileDialog, QHeaderView
)
from database import SessionLocal, init_db
from models import Track, Version
import mutagen  # Install mutagen with pip install mutagen
import os
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

#TODO: 

# Initialize the database
init_db()

# Create a new session
session = SessionLocal()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('Main Window')
        self.setGeometry(100, 100, 800, 600)

        # Create a button to add a song
        self.add_button = QPushButton('Add Song', self)
        self.add_button.clicked.connect(self.add_song)

        # Create a button to delete a song
        self.delete_button = QPushButton('Delete Song', self)
        self.delete_button.clicked.connect(self.delete_song)

        # Create a table to display the songs
        self.table = QTableWidget(self)
        self.populate_table()

        # Arrange the widgets in a layout
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.add_button)
        self.layout.addWidget(self.delete_button)
        self.layout.addWidget(self.table)

        # Create a container widget to hold the layout
        self.container = QWidget(self)
        self.container.setLayout(self.layout)

        self.setCentralWidget(self.container)

    def populate_table(self):
        # Query the database
        tracks = session.query(Track).all()
        self.table.setRowCount(len(tracks))
        self.table.setColumnCount(5)  # Adjust column count based on data
        self.table.setHorizontalHeaderLabels(['Title', 'Artist', 'Length', 'File Path', 'BPM'])  # Set column headers
        for i, track in enumerate(tracks):
            self.table.setItem(i, 0, QTableWidgetItem(track.title))
            self.table.setItem(i, 1, QTableWidgetItem(track.artist))
            self.table.setItem(i, 2, QTableWidgetItem(track.length))
            self.table.setItem(i, 3, QTableWidgetItem(track.file_path))
            self.table.setItem(i, 4, QTableWidgetItem(str(track.BPM)))

    def add_song(self, file_path=None):
        if file_path is None:
            options = QFileDialog.Options()
            file_path, _ = QFileDialog.getOpenFileName(self, "QFileDialog.getOpenFileName()", "", "Audio Files (*.mp3 *.wav *.flac);;All Files (*)", options=options)
        if file_path:
            audio = mutagen.File(file_path, easy=True)  # Extract metadata
            new_track = Track(
                title=audio.get('title', [os.path.basename(file_path)])[0],
                artist=audio.get('artist', ['Unknown'])[0],
                length=str(int(audio.info.length // 60)) + ':' + str(int(audio.info.length % 60)),
                file_path=file_path,
                BPM=0  # Assuming BPM is not available in metadata
            )
            session.add(new_track)
            session.commit()
            self.populate_table()

    def delete_song(self):
        selected_rows = self.table.selectionModel().selectedRows()
        for index in selected_rows:
            track = session.query(Track).all()[index.row()]  # Get the corresponding Track object
            session.delete(track)
        session.commit()
        self.populate_table()

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event):
        for url in event.mimeData().urls():
            file_path = url.toLocalFile()
            self.add_song(file_path=file_path)
    
    def watch_for_songs(self, directory):
        self.event_handler = SongHandler(self)
        self.observer = Observer()
        self.observer.schedule(self.event_handler, directory, recursive=False)
        self.observer.start()
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            self.observer.stop()
        self.observer.join()

class SongHandler(FileSystemEventHandler):
    def __init__(self, window):
        super().__init__()
        self.window = window

    def on_created(self, event):
        if not event.is_directory:
            self.window.add_song(file_path=event.src_path)

    def on_moved(self, event):
        if not event.is_directory:
            self.window.add_song(file_path=event.dest_path)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_window = MainWindow()
    watcher_thread = threading.Thread(target=main_window.watch_for_songs, args=('./path/to/directory',))
    watcher_thread.start()
    main_window.show()
    sys.exit(app.exec_())
