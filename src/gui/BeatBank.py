import datetime
import mutagen, os, time, sys

from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtSql import QSqlTableModel, QSqlDatabase, QSqlQuery
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QTableWidget, QTableWidgetItem, QVBoxLayout, 
    QWidget, QLabel, QFileDialog, QHeaderView, QMessageBox, QHBoxLayout, QFrame,
    QPushButton, QAbstractItemView, QTableView, QAbstractScrollArea, QMenu
)
from PyQt6.QtCore import Qt, QUrl, QMimeData, QTime, QEvent, QDateTime, pyqtSignal

from controllers.database_controller import DatabaseManager
from gui import event_handlers
from gui.edit_track_window import EditTrackWindow
#TODO: get rid of buttons and place in toolbar
#TODO: user stories:
# user story: user can right click a track and select "open file location" to open the folder where the track is located
# user story: user can right click a track and select "edit" to open the edit track window
# user story: user can right click a track and select "delete" to delete the track from the database
# user story: there is a group of items on the context menu called "show similar" when the user highlights this,
    # an option comes up to show similar tracks by bpm or key (eventually tags perhaps) in the filtered table view
# user story: user can right click a track and select "open in ableton" to open the ableton project associated with the track :O
# user story: user can right click a track and select "add to set" that shows open sets or "add to new sets" to add the track to a set
# user story: user can right click a track and select "play audio" to play the audio file in the default audio player
# user story: user can go to settings from the toolbar and "enable/disable" edit mode to reorganize the table
# User story : user can drag and drop a file from this program to another
'''# old imports
from database import SessionLocal, init_db
from business.track_business_model import TrackBusinessModel

from models.user_settings import UserSettings

from gui.edit_track_window import EditTrackWindow

from models.track import Track
from models.version import Version

from controllers import database_controller, track_controller
from controllers.track_controller import TrackController'''

# BeatBank.py (root)/src/gui/BeatBank.py

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.controller = DatabaseManager(self)
        self._updating_cell = False
        self.isEditing = False
        self.init_ui()
        self.table.trackDropped.connect(self.add_track)
        self.editWindow = None
        

    def init_ui(self):
        self.setupWindow()
        self.init_setupLayouts()
        self.init_beat_model()
        self.init_beat_table()
        self.init_filteredTableView() #TODO
        self.setupButtons()
        self.finalizeLayout()
        # Populate the model
        self.model.select() #33333
        
    def setupWindow(self):
        print("Setting up window...")
        self.setWindowTitle('Beat Bank')
        self.setGeometry(100, 100, 1400, 200)
        print("Window set up")

    def init_setupLayouts(self):
        print("Setting up layouts...")
        self.main_layout = QVBoxLayout()
        
        # Create top and table layouts
        self.top_layout = QHBoxLayout()
        self.table_layout = QVBoxLayout()

        # Add top and table layouts to the main layout
        self.main_layout.addLayout(self.top_layout)
        self.main_layout.addLayout(self.table_layout)

        # Create left and right layouts
        self.left_layout = QVBoxLayout()
        self.right_layout = QVBoxLayout()
        self.top_layout.addLayout(self.left_layout)
        self.top_layout.addLayout(self.right_layout)

        print("Layouts initialized.")
            
    def init_beat_model(self):
        print("Initializing model...")
        self.model = QSqlTableModel(self)
        self.model.setTable('tracks')
        self.model.setEditStrategy(QSqlTableModel.EditStrategy.OnFieldChange)
        self.model.select()
        print("Model initialized")

    def init_beat_table(self):
        print("Initializing table...")
        self.table = BeatTable(self)
        self.table.setModel(self.model)
        print("Table initialized")

    def init_filteredTableView(self):
        # TODO: Create a table view widget for the filtered tracks table
        self.filteredTableView = QTableView(self)
        self.filteredTableView.setFrameStyle(QFrame.Shape.Panel | QFrame.Shadow.Sunken)
        # make the table have 2 columns: title and bpm
        # users can select how they want data to be displayed
        # users can select which columns to display
        #users can toggle this table on and off
        #users can select which columns to display  
        
    def setupButtons(self):
        # Refresh button
        self.refresh_button = QPushButton('Refresh', self)
        self.refresh_button.clicked.connect(self.table_refresh)
        self.refresh_button.setIcon(QtGui.QIcon('src/assets/pictures/refresh.png'))
        # 'Add Track' Button
        self.add_button = QPushButton('Add track', self)
        self.add_button.clicked.connect(self.add_track)
        # 'Delete Track' Button
        self.delete_button = QPushButton('Delete track', self)
        self.delete_button.clicked.connect(self.delete_track)
        # 'Edit Track' Button
        self.edit_button = QPushButton('Edit track', self)
        self.edit_button.clicked.connect(self.edit_track)
        # 'Settings' Button
        self.settings_button = QPushButton('Settings', self)
        self.settings_button.clicked.connect(self.open_settings)
        
        # Add widgets to the right/left layouts
        self.left_layout.addWidget(self.refresh_button)
        # TODO: left_layout.addWidget(self.filteredTableView)
        self.right_layout.addWidget(self.add_button)
        self.right_layout.addWidget(self.delete_button)
        self.right_layout.addWidget(self.edit_button)
        self.right_layout.addWidget(self.edit_button)

    def finalizeLayout(self):
        print("Finalizing layout...")
        self.container = QWidget(self)
        self.container.setLayout(self.main_layout)
        self.setCentralWidget(self.container)
        self.table_layout.addWidget(self.table)

# =============================================================================
# MAIN WINDOW FUNCTIONS
# =============================================================================    

    # -------------------------------------------------------------------------
    # FUNCTIONS LINKED TO BUTTONS
    # -------------------------------------------------------------------------
    def add_track(self, path=None):
        print("Adding a new track to the database...")
        if not path:
            path, _ = QFileDialog.getOpenFileName(self, "Select Audio File", "", "Audio Files (*.mp3 *.wav *.flac);;All Files (*)")
            if not path:
                print("No file selected")
                return
        audio = mutagen.File(path, easy=True)
        title = audio.get('title', [os.path.basename(path)])[0]
        artist = audio.get('artist', ['Unknown'])[0]
        length = str(int(audio.info.length // 60)) + ':' + str(int(audio.info.length % 60))
        bpm = 0  # TODO: Implement BPM calculation
        key = 'Unknown'
        date_added = datetime.datetime.now()
        date_created = datetime.datetime.fromtimestamp(os.path.getctime(path))
        notes = None
        path_to_ableton_project = None
        
        # TODO: separate SQL stuff into another function
        # Prepare SQL query for inserting the new track
        query = QSqlQuery()
        query.prepare("INSERT INTO tracks (title, artist, length, bpm, key, date_added, date_created, notes, path_to_ableton_project, file_path) "
                    "VALUES (:title, :artist, :length, :bpm, :key, :date_added, :date_created, :notes, :path_to_ableton_project, :file_path)")

        query.bindValue(":title", title)
        query.bindValue(":artist", artist)
        query.bindValue(":length", length)
        query.bindValue(":bpm", bpm)
        query.bindValue(":key", key)
        query.bindValue(":date_added", QDateTime(date_added).date())
        query.bindValue(":date_created", QDateTime(date_created).date())
        query.bindValue(":notes", notes)
        query.bindValue(":path_to_ableton_project", path_to_ableton_project)
        query.bindValue(":file_path", path)

        # Execute query
        if query.exec():
            print("Track added successfully.")
            self.table_refresh()
        else:
            print("Failed to add track:", query.lastError().text())
    
    def delete_track(self):
        selected_row = self.table.currentIndex().row()
        if selected_row < 0:
            self.show_warning_message("No Selection", "Please select a track to delete.")
            return
        
        reply = QMessageBox.question(self, 'Delete Track', 'Are you sure you want to delete this track?',
                                        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, 
                                        QMessageBox.StandardButton.No)
        
        if reply == QMessageBox.StandardButton.Yes:
            track_id = self.model.record(selected_row).value("id")
            self.delete_from_database(track_id)
            self.table_refresh()
        else:
            print("Track deletion cancelled.")
            return

    def delete_from_database(self, track_id):
        query = QSqlQuery()
        query.prepare("DELETE FROM tracks WHERE id = :id")
        query.bindValue(":id", track_id)
        if query.exec():
            print("Track deleted successfully.")
            self.table_refresh()
        else:
            print("Failed to delete track:", query.lastError().text())


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
       

    
    def edit_track(self):
        print("Editing track...")
        selected_row = self.table.currentIndex().row()
        if selected_row < 0:
            print("No track selected for editing.")
            return
        track_id = self.model.record(selected_row).value("id")
        self.editWindow = EditTrackWindow(track_id)
        self.editWindow.trackEdited.connect(self.table_refresh)
        self.editWindow.show()
        

    def open_settings(self):
        # open the settings window
        pass
    
    # -----------------------------------------------------------------------------
    # FUNCTIONS LINKED TO TABLE
    # -----------------------------------------------------------------------------
    
    def table_refresh(self):
        print("Refreshing table...")
        # Refresh the table
        self.model.select()
        pass
    
    def update_table_row(self, track_id):
        # Update a row in the table
        pass
    

class BeatTable(QTableView):
    trackDropped = pyqtSignal(str)
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.lastClickTime = QTime()
        self.doubleClickInterval = QtWidgets.QApplication.doubleClickInterval()
        self.setAcceptDrops(True)
        self.setDragEnabled(True)
        self.setMinimumHeight(500)
        self.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
    
    
    def handleSingleClick(self, event):
        event_handlers.handleSingleClick(self, event)
    def tableMouseMoveEvent(self, event):
        event_handlers.tableMouseMoveEvent(self, event)
    def startDragOperation(self, item):
        event_handlers.startDragOperation(self, item)
    def dragEnterEvent(self, event):
        event_handlers.dragEnterEvent(self, event)
    def dragMoveEvent(self, event):
        event_handlers.dragMoveEvent(self, event)
    def dropEvent(self, event):
        event_handlers.dropEvent(self, event)
    
    
    #old
    '''def handleDoubleClick(self, event):
        event_handlers.handleDoubleClick(self, event)
    def mousePressEvent(self, event):
        event_handlers.tableMousePressEvent(self, event)'''