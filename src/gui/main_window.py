import re
import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QTableWidget, QTableWidgetItem,
    QPushButton, QVBoxLayout, QWidget, QLabel, QFileDialog, QHeaderView, QMessageBox,
    QHBoxLayout, QFrame
)
from PyQt6 import QtGui
from PyQt6.QtCore import Qt, QUrl, QMimeData, QTime

from controllers import track_controller
from database import SessionLocal, init_db
from business.track_business_model import TrackBusinessModel
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
        self.track_controller = TrackController(self)
        self.user_settings = UserSettings()
        self._updating_cell = False
        self.isEditing = False
        self.init_ui()

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
        self.refresh_button.clicked.connect(self.table_refresh)
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
        self.setup_table()
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
            self.table_refresh()
            self.table.selectRow(self.table.rowCount() - 1)
            self.edit_track()
    
    # Initialize the table 
    def setup_table(self):
        print("Initializing the tracks table...")
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(['Artist', 'Title', 'BPM', 'Length', 'File Path', ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)  # Stretch columns to fill space
        print("Table initialized.")
        self.table_refresh()
    
    # Refresh the entire table    
    def table_refresh(self):
        if self.isEditing:
            return
        self.table.blockSignals(True)
        print("Refreshing table...")
        
        tracks = self.track_controller.get_tracks()
        self.table.setRowCount(len(tracks))

        for i, track in enumerate(tracks):
            print(f"Adding track {track.title} to table...")
            # Visible columns
            self.table.setItem(i, 0, QTableWidgetItem(track.artist))
            self.table.setItem(i, 1, QTableWidgetItem(track.title))
            self.table.setItem(i, 2, QTableWidgetItem(str(track.bpm)))
            self.table.setItem(i, 3, QTableWidgetItem(track.length))
            self.table.setItem(i, 4, QTableWidgetItem(track.file_path))
            
            # Store the track object data in the first column
            print(f"Storing track object data in row {i}...")
            self.table.item(i, 0).setData(Qt.ItemDataRole.UserRole, track)
        self.table.blockSignals(False)
        
    # Takes a track as parameter and updates that row in the table
    def update_table_row(self, row_index):
        try:
            print(f"Updating table row for track in row \'{row_index}\'...")
            track_item = self.table.item(row_index, 0)
            if track_item:
                track = track_item.data(Qt.ItemDataRole.UserRole)
                if track:
                    print(f"Found track \"{track.title}\" at row {row_index}. Updating table row...")
                    self.set_table_row_data(row_index, track)
                else:
                    print("Track object not found in the selected row.")
            else:
                self.handle_track_not_found(track.id)
        except Exception as e:
            print(f"An error occurred: {e}")

    def set_table_row_data(self, row_index, track):
        # Set each cell in the row to the corresponding track attribute
        self.table.setItem(row_index, 0, QTableWidgetItem(track.artist))
        self.table.setItem(row_index, 1, QTableWidgetItem(track.title))
        self.table.setItem(row_index, 2, QTableWidgetItem(str(track.bpm)))  # Assuming the attribute is `bpm` in the model
        self.table.setItem(row_index, 3, QTableWidgetItem(track.length))
        self.table.setItem(row_index, 4, QTableWidgetItem(track.file_path))

    def populate_version_table(self, track):
        versions = self.track_controller.get_versions(track.id)
        self.version_table.setRowCount(len(versions))
        self.version_table.setColumnCount(2)

    # Delete a track from the database
    def delete_track(self):
        print("Deleting track...")
        row_index = self.select_row()
        if row_index is not None:
            track_item = self.table.item(row_index, 0)
            if track_item:
                track = track_item.data(Qt.ItemDataRole.UserRole)
                if track:
                    self.track_controller.delete_track(track.id)
                    self.table_refresh()
                else:
                    print("Track object not found in the selected row.")
            else:
                print("No item found in the selected row.")
        else:
            print("No track selected.")
        

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
        
        row_index = self.select_row()
        print(f"Editing track at row {row_index}..")
        if row_index:
            track_item = self.table.item(row_index, 0)
            if track_item:
                track = track_item.data(Qt.ItemDataRole.UserRole)
                self.track_controller.request_edit_track(track)

    def update_cell(self, item):
        if self._updating_cell or self.isEditing:
            return
        self._updating_cell = True
        try:
            row = item.row()
            column = item.column()
            new_value = item.text()
            track_item = self.table.item(row, 0)
            if track_item:
                track = track_item.data(Qt.ItemDataRole.UserRole)
                if track:
                    self.update_track_attribute(track, column, new_value)
                    self.track_controller.update_track(track)
                    self.table_refresh()
        finally:
            self._updating_cell = False
            # self.table.blockSignals(False)  # FIXME: This causes the table to not update
        
    def update_track_attribute(self, track, column, new_value):
        try:
            if column == 0:
                track.artist = new_value
            elif column == 1:
                track.title = new_value
            elif column == 2:
                track.bpm = float(new_value)
            elif column == 3:
                track.length = new_value
            elif column == 4:
                track.file_path = new_value
            # + Any other columns that are edited...
        except Exception as e:
            print(f"An error occurred: {e}")
            # TODO: Handle the error, like showing a message box to the user
    
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
        #on the table, select the cell at that position
        item = self.table.itemAt(event.pos())
        if item:
            print(f"Item clicked: {item.text()} at row {item.row()}, column {item.column()}")
        self.dragStartPosition = event.pos()
        
    def handleDoubleClick(self, event):
        print("Double click event")
        self.isEditing = True  # Set edit mode flag
        row = self.table.rowAt(event.pos().y())
        column = self.table.columnAt(event.pos().x())
        item = self.table.item(row, column)
        if item:
            print(f"Double clicked on {item.text()} in row {row}, column {column}")
            self.table.setCurrentItem(item)  # Select the item
            item.setFlags(item.flags() | Qt.ItemFlag.ItemIsEditable) # Make the item editable
            self.table.editItem(item)
        else:
            print("No item found at that position.")
        self.isEditing = False  # Unset edit mode flag

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
            print("Adding track " + event.mimeData().urls()[0].toLocalFile() + "...")
            path = event.mimeData().urls()[0].toLocalFile()
            self.track_controller.handle_dropped_file(path)
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

    def handle_track_not_found(self, track_id):
        # Log the error, show a message box, or take other appropriate action
        print(f"Track with ID {track_id} not found.")

    def handle_update_error(self, exception):
        # Log the error, show a message box, or take other appropriate action
        print(f"An error occurred during table update: {exception}")
    
 
    
if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec())
