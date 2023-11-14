import sys
from PyQt6 import QtWidgets, QtGui
from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QLabel, QLineEdit, QPushButton, QVBoxLayout, QWidget, QApplication, QTextEdit
from database import SessionLocal

class EditTrackWindow(QWidget):
    track_updated = pyqtSignal()
    def __init__(self, track=None, session=None):
        super().__init__()
        self.initUI()
        self.track = track
        self.session = session
        
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
        
    # Submits the entered data and commits to the database.
    def submit_edit(self, rowindex):
        print("Submitting data...")
        # Update the track's info
        self.track.title = self.track_title_line_edit.text()
        self.track.artist = self.track_artist_line_edit.text()
        self.track.BPM = float(self.track_bpm_line_edit.text())
        self.track.key = self.track_key_line_edit.text()
        self.track.notes = self.track_notes_text_edit.toPlainText()
        
        try:
            self.session.add(self.track)
            self.session.flush()
            self.session.commit()
            print("Track updated successfully in the database.")
            self.track_updated.emit()
        except Exception as e:
            print(f"An error occurred: {e}")
            self.session.rollback()  # Rollback in case of error
        finally:
            #TODO: signal to refresh the database
            self.session.close()
            # Close the window
            self.close()
        
        
    def setTrackInfo(self, track):
        self.track_title_line_edit.setText(track.title)
        self.track_artist_line_edit.setText(track.artist)
        self.track_bpm_line_edit.setText(str(track.BPM))
        self.track_key_line_edit.setText(track.key)
        self.track_notes_text_edit.setText(track.notes)
