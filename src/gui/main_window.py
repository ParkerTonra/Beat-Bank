import PyQt5
import sys
import os
import threading
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QTableWidget, QTableWidgetItem,
    QPushButton, QVBoxLayout, QWidget, QLabel, QFileDialog, QHeaderView, QMessageBox
)
from PyQt5 import QtGui
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
        
        # Create a refresh button
        self.refresh_button = QPushButton('Refresh', self)
        self.refresh_button.clicked.connect(self.full_update_table)
        # set the icon to src/assets/pictures/refresh.png
        self.refresh_button.setIcon(QtGui.QIcon('src/assets/pictures/refresh.png'))

        # Arrange the widgets in a layout
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.refresh_button)
        self.layout.addWidget(self.add_button)
        self.layout.addWidget(self.delete_button)
        self.layout.addWidget(self.edit_button)
        self.layout.addWidget(self.table)

        # Create a container widget to hold the layout
        self.container = QWidget(self)
        self.container.setLayout(self.layout)

        self.setCentralWidget(self.container)

    # unused, but could be used to refresh the entire table    
    def full_update_table(self):
        session = SessionLocal()
        tracks = session.query(Track).all()
        self.table.setRowCount(len(tracks))
        for i, track in enumerate(tracks):
            self.table.setItem(i, 0, QTableWidgetItem(track.artist))
            self.table.setItem(i, 1, QTableWidgetItem(track.title))
            self.table.setItem(i, 2, QTableWidgetItem(str(track.BPM)))
            self.table.setItem(i, 3, QTableWidgetItem(track.length))
            self.table.setItem(i, 4, QTableWidgetItem(track.file_path))
        session.close()
        
    # Takes a track as parameter and updates that row in the table
    def update_table(self, track, row_index):
        session = SessionLocal()
        # Query the database to find the track with the same id as the passed track object
        updated_track = session.query(Track).filter(Track.id == track.id).first()
        if updated_track:
            # Update the table directly using the known row index
            self.table.setItem(row_index, 0, QTableWidgetItem(updated_track.artist))
            self.table.setItem(row_index, 1, QTableWidgetItem(updated_track.title))
            self.table.setItem(row_index, 2, QTableWidgetItem(str(updated_track.BPM)))
            self.table.setItem(row_index, 3, QTableWidgetItem(updated_track.length))
            self.table.setItem(row_index, 4, QTableWidgetItem(updated_track.file_path))
        session.close()
    
    def populate_table(self):
        session = SessionLocal()
        # Query the database
        tracks = session.query(Track).all()
        self.table.setRowCount(len(tracks))
        self.table.setColumnCount(5)  # Adjust column count based on data
        self.table.setHorizontalHeaderLabels(['Artist', 'Title', 'BPM', 'Length', 'File Path', ])  # Set column headers
        for i, track in enumerate(tracks):
            self.table.setItem(i, 0, QTableWidgetItem(track.artist))
            self.table.setItem(i, 1, QTableWidgetItem(track.title))
            self.table.setItem(i, 2, QTableWidgetItem(str(track.BPM)))
            self.table.setItem(i, 3, QTableWidgetItem(track.length))
            self.table.setItem(i, 4, QTableWidgetItem(track.file_path))
        session.close()

    def add_track(self):
        session = SessionLocal()
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
        session.close()

    def delete_track(self):
        session = SessionLocal()
        selected_rows = self.table.selectionModel().selectedRows()
        for index in selected_rows:
            track = session.query(Track).all()[index.row()]  # Get the corresponding Track object
            session.delete(track)
        session.commit()
        self.populate_table()
        session.close()
    
    def edit_track(self):
        print("Editing track...")
        session = SessionLocal()
        # Get the selected row
        selected_rows = self.table.selectionModel().selectedRows()
        row_index = None
        
        if selected_rows:
            row_index = selected_rows[0].row()
        else:
            # Check if any items are selected
            selected_items = self.table.selectionModel().selection()
            if selected_items:
                print("No Row Selected. Selected items: ", selected_items)
                row_index = selected_items[0].indexes()[0].row()
                
        if row_index is not None:
            with SessionLocal() as session:
                 track = session.query(Track).all()[row_index]
                 self.edit_window = EditTrackWindow(track, session)
                 self.edit_window.setTrackInfo(track)
                 self.edit_window.show()
        
        else:
            self.show_warning_message("No Track Selected", "Please select a track to edit.")
    
    # Function to show a warning message
    def show_warning_message(self, title, message):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Warning)
        msg.setWindowTitle(title)
        msg.setText(message)
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec_()
        
        

if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())
