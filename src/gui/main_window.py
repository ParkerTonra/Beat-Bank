import re
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
from PyQt6.QtCore import Qt, QUrl, QMimeData, QTime
from controllers import track_controller
from database import SessionLocal, init_db
from models.track_business_model import TrackBusinessModel
from models.track import Track
from models.version import Version
from controllers.track_controller import TrackController
from gui.edit_track_window import EditTrackWindow
import mutagen  # Install mutagen with pip install mutagen
import os
import time
from PyQt6.QtWidgets import QAbstractItemView
from PyQt6.QtGui import QDrag
from PyQt6 import QtWidgets
from models.user_settings import UserSettings
#TODO: remember settings for window size / other user settings and position from cache or something
# Initialize the database
init_db()

# =============================================================================
# Main Window GUI
# =============================================================================
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.track_controller = TrackController(self)
        self.user_settings = UserSettings()

    def init_ui(self):
        print("Initializing UI for main window...")
        self.setWindowTitle('Beat Bank')
        self.setGeometry(100, 100, 1400, 200)
        
        self.lastClickTime = QTime()
        self.doubleClickInterval = QtWidgets.QApplication.doubleClickInterval()
        
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
        self.version_table = QTableWidget()
        self.version_table.setFrameStyle(QFrame.Shape.Panel | QFrame.Shadow.Sunken)
        # Give the table two columns: version name and file path
        self.version_table.setColumnCount(2)
        self.version_table.setHorizontalHeaderLabels(['Version Name', 'File Path'])
        self.version_table.setMinimumSize(100, 120)  # Adjust size as needed
        self.version_table.setMaximumHeight(150)
        left_layout.addWidget(self.version_table)
        
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
        self.table.itemChanged.connect(self.update_cell)
        
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
    
    # Add a new track as a Track object to the database
    def add_track(self, path=None):
        if self.ask_if_new_track(path) is False:
            print("TODO. Track not added.")
            # add_new_version(path)
            return
        if path:
            file_name = path
        else:
            file_name, _ = QFileDialog.getOpenFileName(self, "Select Audio File", "", "Audio Files (*.mp3 *.wav *.flac);;All Files (*)")
        if file_name:
            self.track_controller.add_track(file_name)
            self.populate_table()
            self.table.selectRow(self.table.rowCount() - 1)
            self.edit_track()

    
    # Refresh the entire table    
    def full_update_table(self):
        tracks = self.track_controller.get_tracks()
        self.table.setRowCount(len(tracks))
        # developer mode #TODO: every column shows up

        # user mode
        for i, track in enumerate(tracks):
            self.table.setItem(i, 0, QTableWidgetItem(track.artist))
            self.table.setItem(i, 1, QTableWidgetItem(track.title))
            self.table.setItem(i, 2, QTableWidgetItem(str(track.bpm)))
            self.table.setItem(i, 3, QTableWidgetItem(track.length))
            self.table.setItem(i, 4, QTableWidgetItem(track.file_path))
        
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
            self.table.setItem(i, 2, QTableWidgetItem(str(track.bpm)))
            self.table.setItem(i, 3, QTableWidgetItem(track.length))
            self.table.setItem(i, 4, QTableWidgetItem(track.file_path))
        session.close()
    
    def populate_version_table(self, track):
        with SessionLocal as session:
            versions = session.query(Version).filter(Version.track_id == track.id).all()
            self.version_table.setRowCount(len(versions))
            self.version_table.setColumnCount(2)

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
    
    def update_cell(self, item):
        row = item.row()
        column = item.column()
        new_value = item.text()
        self.update_database(row, column, new_value)
    
    def update_database(self, row, column, new_value):
        session = SessionLocal()
        try:
            track = session.query(Track).all()[row]
            
            if column == 0:
                track.artist = new_value
            elif column == 1:
                track.title = new_value
            elif column == 2:
                try:
                    track.bpm = float(new_value)
                except ValueError:
                    raise ValueError("BPM must be a number.")
            elif column == 3:
                if not re.match(r'^\d+:\d+$', new_value):
                    raise ValueError("Length must be in format 'xx:xx'.")
                track.length = new_value
            elif column == 4:
                track.file_path = new_value

            session.commit()
        except Exception as e:
            session.rollback()
            print(f"An error occurred: {e}")
            # Here you can handle the error, like showing a message box to the user
        finally:
            session.close()
    
    # TODO: Implement settings function
    def open_settings(self):
        print("Settings")
        #rearrange mode
        # local library or path mode
        # dark mode off (WHY WOULD YOU DO THIS)


    # drag and drop
    def tableMousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            current_time = QTime.currentTime()

            if not self.lastClickTime.isNull() and \
               self.lastClickTime.msecsTo(current_time) < self.doubleClickInterval:
                self.handleDoubleClick(event)
            else:
                self.handleSingleClick(event)
            
            self.lastClickTime = current_time
         
    def handleSingleClick(self, event):
        print("Single click event")
        #on the table, select the cell at that position
        item = self.table.itemAt(event.pos())
        self.table.setCurrentItem(item)
        self.dragStartPosition = event.pos()
        
    def handleDoubleClick(self, event):
        print("Double click event")
        item = self.table.itemAt(event.pos())
        self.table.setCurrentItem(item)
        item.setFlags(item.flags() | Qt.ItemFlag.ItemIsEditable)
        self.table.editItem(item)
    
    def tableMouseMoveEvent(self, event):
        if not (event.buttons() & Qt.MouseButton.LeftButton):
            return
        if ((event.pos() - self.dragStartPosition).manhattanLength() < QApplication.startDragDistance()):
            print("Mouse move event")
            return

        item = self.table.itemAt(self.dragStartPosition)
        if item and self.isDraggableCell(item):
            print("Draggable cell")
            self.startDragOperation(item)

    def startDragOperation(self, item):
        mime_data = QMimeData()
        mime_data.setUrls([QUrl.fromLocalFile(item.text())])

        drag = QDrag(self.table)
        drag.setMimeData(mime_data)
        drag.exec(Qt.DropAction.CopyAction | Qt.DropAction.MoveAction)

    def isDraggableCell(self, item):
        # if the column is the file path column
        return item.column() == 4

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
                # query the database to see if this file is already in the database
                session = SessionLocal()
                if self.track_controller.already_in_database(path):
                    session.close()
                    self.show_warning_message("Track Already in Database", "This track is already in the database.")
                    return
                self.add_track(path)
            except Exception as e:
                print(f"An error occurred: {e} .. unable to add track to database.")
            event.accept() # Allow the drop
        else:
            print("Error. Unable to add track to database. Is the file an audio file?")
            event.ignore()

    # Ask user if the new track is a new version of an existing track
    def ask_if_new_track(self, path):
        # query the database to see if this file is already in the database
        if self.track_controller.already_in_database(path):
            self.show_warning_message("Track Already in Database", "This file is already in the database.")
            return
        else:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Icon.Question)
            msg.setWindowTitle("New Track? or new version?")
            msg.setText("Is this a new track? Select no if another version is already in the database.")
            msg.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            msg.setDefaultButton(QMessageBox.StandardButton.Yes)
            response = msg.exec()
            if response == QMessageBox.StandardButton.Yes:
                return True
            else:
                return False

    # Show a warning message
    def show_warning_message(self, title, message):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Icon.Warning)
        msg.setWindowTitle(title)
        msg.setText(message)
        msg.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg.exec()

    
if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec())
