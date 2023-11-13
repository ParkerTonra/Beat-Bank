import sys
from PyQt5 import QtWidgets, QtGui
from PyQt5.QtWidgets import QLabel, QLineEdit, QPushButton, QVBoxLayout, QWidget, QApplication, QTextEdit


class EditTrackWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        
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

        # Connect the button's click signal to the submit_data method
        self.submitButton.clicked.connect(self.submit_data)

        self.setWindowTitle('Edit Track')
        
    # Submit data - called when someone clicks the submit button.
    def submit_data(self):
        data = self.lineEdit.text()
        print(f"Data entered: {data}")
        # Now you can use 'data' anywhere in your code
    
    def setTrackInfo(self, track):
        # Update label texts with track info
        # T)T)T0d0 todo todo todo
        self.track_title_line_edit.setText(track.title)
        self.track_artist_line_edit.setText(track.artist)
        self.track_bpm_line_edit.setText(str(track.BPM))
        self.track_key_line_edit.setText(track.key)
        self.track_notes_text_edit.setText(track.notes)
        
        #self.filePathLabel.setText(f"File Path: {track.file_path}")
        #self.bpmLabel.setText(f"BPM: {track.BPM}")
        

# app = QtWidgets.QApplication(sys.argv)
# windows = QtWidgets.QWidget()
# windows.resize(500,500)
# windows.move(100,100)

# windows.setWindowTitle('Edit Track')
# windows.setWindowIcon(QtGui.QIcon('icon.png'))
# windows.show()
# sys.exit(app.exec_())