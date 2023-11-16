import PyQt6
import sys
import os
import threading
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QTableWidget, QTableWidgetItem,
    QPushButton, QVBoxLayout, QWidget, QLabel, QFileDialog, QHeaderView, QMessageBox,
    QHBoxLayout, QFrame
)
from PyQt6 import QtGui
from PyQt6.QtCore import Qt, QUrl, QMimeData
from database import SessionLocal, init_db
from models import Track, Version
from gui.edit_track_window import EditTrackWindow
import mutagen  # Install mutagen with pip install mutagen
import os
import time
from PyQt6.QtWidgets import QAbstractItemView
from PyQt6.QtGui import QDrag

# Initialize the database
init_db()

# =============================================================================
# Main Window GUI
# =============================================================================
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        print("Initializing UI for main window...")
        self.setWindowTitle('Beat Bank')
        self.setGeometry(100, 100, 1400, 200)
        
        # -----------------------------------------------------------------------------
        # LEFT COLUMN LAYOUT
        # ----------------------------------------------------------------------------- 
        
        # Create the layout object
        left_layout = QVBoxLayout()
        
        # Refresh button
        self.refresh_button = QPushButton('Refresh', self)
        self.refresh_button.clicked.connect(self.full_update_table)
        self.refresh_button.setIcon(QtGui.QIcon('src/assets/pictures/refresh.png'))
        left_layout.addWidget(self.refresh_button)
        
        # Drag and drop TODO: Implement drag and drop
        self.drag_drop_area = QLabel("Drag and Drop Area", self, alignment=Qt.AlignmentFlag.AlignCenter)
        self.drag_drop_area.setFrameStyle(QFrame.Shape.Panel | QFrame.Shadow.Sunken)
        # self.drag_drop_area.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.drag_drop_area.setMinimumSize(100, 120)  # Adjust size as needed
        self.drag_drop_area.setMaximumHeight(150)
        self.drag_drop_area.setAcceptDrops(True)
        left_layout.addWidget(self.drag_drop_area)
        
        # -----------------------------------------------------------------------------
        # RIGHT COLUMN LAYOUT
        # -----------------------------------------------------------------------------    

        # Create the layout object
        right_layout = QVBoxLayout()
        
        # 'Add Track' Button
        self.add_button = QPushButton('Add track', self)
        self.add_button.clicked.connect(self.add_track)
        right_layout.addWidget(self.add_button)
        
        # 'Delete Track' Button
        self.delete_button = QPushButton('Delete track', self)
        self.delete_button.clicked.connect(self.delete_track)
        right_layout.addWidget(self.delete_button)
        
        # 'Edit Track' Button
        self.edit_button = QPushButton('Edit track', self)
        self.edit_button.clicked.connect(self.edit_track)
        right_layout.addWidget(self.edit_button)
        
        # 'Settings' Button
        self.edit_button = QPushButton('Settings', self)
        self.edit_button.clicked.connect(self.open_settings)
        right_layout.addWidget(self.edit_button)
        
        # -----------------------------------------------------------------------------
        # TOP COLUMN LAYOUT (R/L)
        # ----------------------------------------------------------------------------- 
        
        top_layout = QHBoxLayout()
        top_layout.addLayout(left_layout)
        top_layout.addLayout(right_layout)
        
        # -----------------------------------------------------------------------------
        # TABLE LAYOUT FOR DATABASE
        # -----------------------------------------------------------------------------
        
        # Create the layout object
        table_layout = QVBoxLayout()
        
        # Create the table object
        self.table = QTableWidget(self)
        self.table.setMinimumHeight(500)
        
        # Drag and drop
        self.table.setAcceptDrops(True)
        self.table.setDragEnabled(True)
        
        # Connect mouse events
        self.table.mousePressEvent = self.tableMousePressEvent
        self.table.mouseMoveEvent = self.tableMouseMoveEvent
        
        #populate the table
        self.populate_table()
        table_layout.addWidget(self.table)
        
        # -----------------------------------------------------------------------------
        # MAIN LAYOUT
        # -----------------------------------------------------------------------------

        main_layout = QVBoxLayout()
        main_layout.addLayout(top_layout)
        main_layout.addLayout(table_layout)

        # Create a container widget to hold the layout
        self.container = QWidget(self)
        self.container.setLayout(main_layout)

        self.setCentralWidget(self.container)


    # =============================================================================
    # MAIN WINDOW FUNCTIONS
    # =============================================================================
    
    # Refresh the entire table    
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
    
    # Refreshes the whole table
    def populate_table(self):
        session = SessionLocal()
        # Query the database
        tracks = session.query(Track).all()
        self.table.setRowCount(len(tracks))
        self.table.setColumnCount(5)  # Adjust column count based on data
        self.table.setHorizontalHeaderLabels(['Artist', 'Title', 'BPM', 'Length', 'File Path', ])  # Set column headers
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)  # Stretch columns to fill space
        for i, track in enumerate(tracks):
            self.table.setItem(i, 0, QTableWidgetItem(track.artist))
            self.table.setItem(i, 1, QTableWidgetItem(track.title))
            self.table.setItem(i, 2, QTableWidgetItem(str(track.BPM)))
            self.table.setItem(i, 3, QTableWidgetItem(track.length))
            self.table.setItem(i, 4, QTableWidgetItem(track.file_path))
        session.close()

    # Add a new track as a Track object to the database
    def add_track(self, path=None):
        if path:
            file_name = path
        else:
            file_name, _ = QFileDialog.getOpenFileName(self, "Select Audio File", "", "Audio Files (*.mp3 *.wav *.flac);;All Files (*)")
        session = SessionLocal()
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
            # select the row of the newly added track
            self.table.selectRow(self.table.rowCount() - 1)
            #edit_track on the new track
            self.edit_track()
        session.close()

    # Delete a track from the database
    def delete_track(self):
        session = SessionLocal()
        row_index = self.select_row()
        track = session.query(Track).all()[row_index]
        session.delete(track)
        session.commit()
        self.full_update_table()
        session.close()
    
    # Select row from item selected
    def select_row(self):
        # Get the selected row
        selected_rows = self.table.selectionModel().selectedRows()
        
        if selected_rows:
            return selected_rows[0].row()
        
        # Check if any items are selected
        selected_items = self.table.selectionModel().selection()
        if selected_items:
            row_index = selected_items[0].indexes()[0].row()
            self.table.selectRow(row_index)
            return row_index
        
        self.show_warning_message("No Track Selected", "Please select a track to edit.")
        return None
    
    # Edit track metadata
    def edit_track(self):
        print("Editing track...")
        session = SessionLocal()

        # Get the selected row
        row_index = self.select_row()
        if row_index is not None:
            with SessionLocal() as session:
                track = session.query(Track).all()[row_index]
                self.edit_window = EditTrackWindow(track, session)
                self.edit_window.track_updated.connect(self.full_update_table)
                self.edit_window.setTrackInfo(track)
                self.edit_window.show()

    # TODO: Implement settings function
    def open_settings(self):
        print("Settings")

    # Show a warning message
    def show_warning_message(self, title, message):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Warning)
        msg.setWindowTitle(title)
        msg.setText(message)
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec()

    # drag and drop
    def tableMousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.dragStartPosition = event.pos()

    def tableMouseMoveEvent(self, event):
        if not (event.buttons() & Qt.MouseButton.LeftButton):
            return
        if ((event.pos() - self.dragStartPosition).manhattanLength() < QApplication.startDragDistance()):
            return

        item = self.table.itemAt(self.dragStartPosition)
        if item and self.isDraggableCell(item):
            self.startDragOperation(item)

    def startDragOperation(self, item):
        mime_data = QMimeData()
        mime_data.setUrls([QUrl.fromLocalFile(item.text())])

        drag = QDrag(self.table)
        drag.setMimeData(mime_data)
        drag.exec(Qt.DropAction.CopyAction | Qt.DropAction.MoveAction)

    def isDraggableCell(self, item):
        # Your logic to determine if the cell should be draggable
        return # item.row() == your_draggable_row and item.column() == your_draggable_column

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dragMoveEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event):
        # if file or link is dropped and it's an audio file
        if event.mimeData().hasUrls() and event.mimeData().urls()[0].toLocalFile().endswith(('.mp3', '.wav', '.flac')):
            print("Adding track " + event.mimeData().urls()[0].toLocalFile() + " to database...")
            try:
                path = event.mimeData().urls()[0].toLocalFile()
                self.add_track(path)
            except Exception as e:
                print(f"An error occurred: {e} .. unable to add track to database.")
            event.accept() # Allow the drop
        else:
            print("Error. Unable to add track to database. Is the file an audio file?")
            event.ignore()
    
if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec())
