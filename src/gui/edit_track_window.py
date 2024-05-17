import sys
from PyQt6 import QtWidgets, QtGui
from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QLabel, QLineEdit, QPushButton, QVBoxLayout, QWidget, QApplication, QTextEdit
from PyQt6.QtSql import QSqlQuery

class EditTrackWindow(QWidget):
    trackEdited = pyqtSignal()
    def __init__(self, track_id):
        super().__init__()
        self.track_id = track_id
        self.initUI()
        track_record = self.get_track_record(track_id)
        self.setTrackInfo(track_record)

    def initUI(self):
        print("Initializing UI for edit window...")
        # Create widgets for label and text entry
        # Track Title
        self.track_title_label = QLabel("Title: ", self)
        self.track_title_line_edit = QLineEdit(self)

        # Track Artist
        self.track_artist_label = QLabel("Artist: ", self)
        self.track_artist_line_edit = QLineEdit(self)

        # Track BPM
        self.track_bpm_label = QLabel("BPM: ", self)
        self.track_bpm_line_edit = QLineEdit(self)

        # Track Key
        self.track_key_label = QLabel("Key: ", self)
        self.track_key_line_edit = QLineEdit(self)
        
        # Track Notes
        self.track_notes_label = QLabel("Notes: ", self)
        self.track_notes_text_edit = QTextEdit(self)
        self.track_notes_text_edit.setFixedHeight(80)

        # Submit button
        self.submitButton = QPushButton("Submit", self)

        # Form layout
        layout = QVBoxLayout()
        
        # Add the widgets to the layout
        layout.addWidget(self.track_title_label)
        layout.addWidget(self.track_title_line_edit)
        layout.addWidget(self.track_artist_label)
        layout.addWidget(self.track_artist_line_edit)
        layout.addWidget(self.track_bpm_label)
        layout.addWidget(self.track_bpm_line_edit)
        layout.addWidget(self.track_key_label)
        layout.addWidget(self.track_key_line_edit)
        layout.addWidget(self.track_notes_label)
        layout.addWidget(self.track_notes_text_edit)
        layout.addWidget(self.submitButton)

        # Set the layout on the application's window
        self.setLayout(layout)

        # Connect the button's click signal to the submit_edit method
        self.submitButton.clicked.connect(self.submit_edit)

        self.setWindowTitle('Edit Track')

    def get_track_record(self, track_id):
        print("Fetching track record...")
        query = QSqlQuery()
        query.exec(f"SELECT * FROM tracks WHERE id = {track_id}")
        if query.next():
            return query.record()
        else:
            print("Track not found")
            return None


    def submit_edit(self):
        print("Submitting data...")
        query = QSqlQuery()
        query.prepare("UPDATE tracks SET title = :title, artist = :artist, bpm = :bpm, "
                      "key = :key, notes = :notes WHERE id = :id")
        query.bindValue(":title", self.track_title_line_edit.text())
        query.bindValue(":artist", self.track_artist_line_edit.text())
        query.bindValue(":bpm", float(self.track_bpm_line_edit.text()))
        query.bindValue(":key", self.track_key_line_edit.text())
        query.bindValue(":notes", self.track_notes_text_edit.toPlainText())
        query.bindValue(":id", self.track_id)

        if query.exec():
            print("Track updated successfully.")
            self.trackEdited.emit()
        else:
            print("Failed to update track:", query.lastError().text())

        self.close()

    def setTrackInfo(self, track):
        # Assuming track is a QSqlRecord or similar
        self.track_title_line_edit.setText(track.value("title"))
        self.track_artist_line_edit.setText(track.value("artist"))
        self.track_bpm_line_edit.setText(str(track.value("bpm")))
        self.track_key_line_edit.setText(track.value("key"))
        self.track_notes_text_edit.setText(track.value("notes"))