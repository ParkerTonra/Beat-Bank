import sys
import os
import threading
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QTableWidget, QTableWidgetItem,
    QPushButton, QVBoxLayout, QWidget, QLabel, QFileDialog, QHeaderView
)
from database import SessionLocal, init_db
from models import Track, Version
from gui.edit_track_window import EditTrackWindow
import mutagen  # Install mutagen with pip install mutagen
import os
import time

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
        print("Initializing UI for main window...")
        self.setWindowTitle('Main Window')
        self.setGeometry(100, 100, 800, 600)

        # Create a button to add a track
        self.add_button = QPushButton('Add track', self)
        self.add_button.clicked.connect(self.add_track)

        # Create a button to delete a track
        self.delete_button = QPushButton('Delete track', self)
        self.delete_button.clicked.connect(self.delete_track)
        
        # Create a button to edit a track
        self.edit_button = QPushButton('Edit track', self)
        self.edit_button.clicked.connect(self.edit_track)

        # Create a table to display the tracks
        self.table = QTableWidget(self)
        self.populate_table()

        # Arrange the widgets in a layout
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.add_button)
        self.layout.addWidget(self.delete_button)
        self.layout.addWidget(self.edit_button)
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

    def add_track(self):
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getOpenFileName(self, "QFileDialog.getOpenFileName()", "", "Audio Files (*.mp3 *.wav *.flac);;All Files (*)", options=options)
        if file_name:
            audio = mutagen.File(file_name, easy=True)  # Extract metadata
            new_track = Track(
                title=audio.get('title', [os.path.basename(file_name)])[0],
                artist=audio.get('artist', ['Unknown'])[0],
                length=str(int(audio.info.length // 60)) + ':' + str(int(audio.info.length % 60)),
                file_path=file_name,
                BPM=0  # Assuming BPM is not available in metadata
            )
            session.add(new_track)
            session.commit()
            self.populate_table()

    def delete_track(self):
        selected_rows = self.table.selectionModel().selectedRows()
        for index in selected_rows:
            track = session.query(Track).all()[index.row()]  # Get the corresponding Track object
            session.delete(track)
        session.commit()
        self.populate_table()
    
    def edit_track(self):
        print("Editing track...")
        self.edit_window = EditTrackWindow()
        track = session.query(Track).all()[self.table.selectionModel().selectedRows()[0].row()]
        self.edit_window.setTrackInfo(track)
        self.edit_window.show()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())
