import datetime
import platform
import subprocess
import mutagen, os, time, sys
import pickle

from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtSql import QSqlTableModel, QSqlDatabase, QSqlQuery
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QTableWidget, QTableWidgetItem, QVBoxLayout, 
    QWidget, QLabel, QFileDialog, QHeaderView, QMessageBox, QHBoxLayout, QFrame,
    QPushButton, QAbstractItemView, QTableView, QAbstractScrollArea, QMenu, QDialog, QLineEdit, QInputDialog,
    QStyledItemDelegate
)
from PyQt6.QtCore import Qt, QUrl, QMimeData, QTime, QEvent, QDateTime, pyqtSignal, QSettings, QSortFilterProxyModel
# import pyqt6 QAction
from PyQt6.QtGui import QAction, QBrush, QColor

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import webbrowser
import threading

from controllers.database_controller import DatabaseManager
from gui import event_handlers
from gui.edit_track_window import EditTrackWindow
#TODO: Fix google drive integration
#TODO: Figure out way column's won't resize (works on mac, not on windows)
#TODO: make file location persistent
#TODO: user stories:
# user story: user can right click a track and select "open file location" to open the folder where the track is located
# user story: user can store the music DB on google drive.
# user story: there is a group of items on the context menu called "show similar" when the user highlights this,
    # an option comes up to show similar tracks by bpm or key (eventually tags perhaps) in the filtered table view
# user story: user can right click a track and select "open in ableton" to open the ableton project associated with the track :O
# user story: user can right click a track and select "add to set" that shows open sets or "add to new sets" to add the track to a set
# user story: user can right click a track and select "play audio" to play the audio file in the default audio player
# user story: user can go to settings from the toolbar and "enable/disable" edit mode to reorganize the table
# User story : user can drag and drop a file from this program to another
# user story: users can change the width of the columns, and the changes are saved
    #user story: users can lock column width from settings menu
    
#COMPLETED:
# user story: users can change the order of the columns, and the changes are saved
    #user story: users can lock column order from settings menu
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
    # -------------------------------------------------------------------------
    # Initialization / UI Setup
    # -------------------------------------------------------------------------
    def __init__(self):
        super().__init__()
        self.controller = DatabaseManager(self)
        self._updating_cell = False
        self.isEditing = False
        self.init_ui()
        self.table.trackDropped.connect(self.add_track)
        self.editWindow = None
        self.init_google_drive()

    def init_ui(self):
        self.setupWindow()
        self.init_setupLayouts()
        self.init_beat_model()
        self.init_beat_table()
        self.restore_table_state()
        self.init_filteredTableView() #TODO
        # self.setupButtons()
        self.init_menu_bar()
        self.finalizeLayout()
        # Populate the model
        self.model.select() #33333
        
    def setupWindow(self):
        print("Setting up window...")
        self.setWindowTitle('Beat Bank')
        self.setGeometry(100, 100, 1400, 200)
        print("Window set up")

    def finalizeLayout(self):
        print("Finalizing layout...")
        self.container = QWidget(self)
        self.container.setLayout(self.main_layout)
        self.setCentralWidget(self.container)
        self.table_layout.addWidget(self.table)
    
    # -------------------------------------------------------------------------
    # UI component initialization
    # -------------------------------------------------------------------------
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
        
        # Initialize the QSortFilterProxyModel
        self.proxyModel = QSortFilterProxyModel(self)
        self.proxyModel.setSourceModel(self.model)  # Set the source model
        
        print("Model initialized")

    def init_beat_table(self):
        print("Initializing table...")
        self.table = BeatTable(self)
        self.delegate = InvalidFileDelegate(self.table)
        self.table.setItemDelegate(self.delegate)
        self.table.setModel(self.proxyModel)
        self.table.setSortingEnabled(True)
        # Hide unnecessary columns
        self.table.hideColumn(0)  
        self.table.hideColumn(8)  
        self.table.hideColumn(10) 
        #refresh
        self.table_refresh()
        
        print("Table initialized")
        
    def init_google_drive(self):
        print("Checking for existing Google Drive credentials...")
        credentials = self.load_credentials()
        if credentials and credentials.valid:
            print("Credentials loaded.")
        elif credentials and credentials.expired and credentials.refresh_token:
            print("Refreshing credentials...")
            try:
                credentials.refresh(Request())
                self.save_credentials(credentials)  # Make sure to save the refreshed credentials
                print("Credentials refreshed and saved.")
            except Exception as e:
                print(f"Error refreshing credentials: {e}")
                return
        else:
            print("No valid credentials available.")
            return

        self.gdrive_service = build('drive', 'v3', credentials=credentials)

    def init_filteredTableView(self):
        # TODO: Create a table view widget for the filtered tracks table
        self.filteredTableView = QTableView(self)
        self.filteredTableView.setFrameStyle(QFrame.Shape.Panel | QFrame.Shadow.Sunken)
        # make the table have 2 columns: title and bpm
        # users can select how they want data to be displayed
        # users can select which columns to display
        #users can toggle this table on and off
        #users can select which columns to display  
    
    # -------------------------------------------------------------------------
    # Menu bar and Actions
    # -------------------------------------------------------------------------
    def init_menu_bar(self):
        # Create Menu Bar
        menu_bar = self.menuBar()

        # Add Menus
        file_menu = menu_bar.addMenu("&File")
        edit_menu = menu_bar.addMenu("&Edit")
        view_menu = menu_bar.addMenu("&View")
        settings_menu = menu_bar.addMenu("&Settings")
        tools_menu = menu_bar.addMenu("&Tools")
        help_menu = menu_bar.addMenu("&Help")
        columns_menu = view_menu.addMenu("&Columns")
        self.init_columns_submenu(columns_menu)

        # File Menu Actions
        exit_action = QAction("&Exit", self)
        exit_action.triggered.connect(sys.exit)
        
        add_track_action = QAction("&Add Track", self)
        add_track_action.triggered.connect(self.add_track)
        
        refresh_action = QAction("&Refresh", self)
        refresh_action.triggered.connect(self.table_refresh)
        
        gdrive_action = QAction("&Google Drive Sign in", self)
        gdrive_action.triggered.connect(self.authenticate_user)
        
        gdrive_folder_action = QAction("&Folder", self)
        gdrive_folder_action.triggered.connect(self.find_or_create_beatbank_folder)

        file_menu.addAction(add_track_action)
        file_menu.addAction(refresh_action)
        file_menu.addAction(exit_action)
        file_menu.addAction(gdrive_action)
        file_menu.addAction(gdrive_folder_action)

        # Edit Menu Actions
        edit_track_action = QAction("&Edit Track", self)
        edit_track_action.triggered.connect(self.edit_track)
        
        delete_track_action = QAction("&Delete Track", self)
        delete_track_action.triggered.connect(self.delete_track)

        edit_menu.addAction(edit_track_action)
        edit_menu.addAction(delete_track_action)
        
        # Settings Menu Actions
        toggle_reorder_action = QAction("&Allow reorder", self, checkable=True)
        toggle_reorder_action.triggered.connect(self.toggle_reorder)
        
        print_service_action = QAction("&Print Service Object", self)
        print_service_action.triggered.connect(self.print_service_object)
        
        choose_folder_action = QAction("&Choose Folder", self)
        choose_folder_action.triggered.connect(self.list_and_choose_folder)
        
        settings_menu.addAction(toggle_reorder_action)
        settings_menu.addAction(print_service_action)
        settings_menu.addAction(choose_folder_action)
        

        

        # View Menu Actions
        show_similar_tracks_action = QAction("Always Show Similar Tracks Table", self, checkable=True)
        show_similar_tracks_action.toggled.connect(self.toggle_similar_tracks)
        
        
        view_menu.addAction(show_similar_tracks_action)

        # Tools Menu Actions
        check_integrity_action = QAction("Check Song File Integrity", self)
        check_integrity_action.triggered.connect(self.check_song_file_integrity)
        tools_menu.addAction(check_integrity_action)
        
        # Help Menu Actions
        read_me_action = QAction("Read Me", self)
        # Connect read_me_action to the appropriate slot
        help_menu.addAction(read_me_action)

    def init_columns_submenu(self, columns_menu):
        for i in range(self.table.model().columnCount()):
            column_name = self.table.model().headerData(i, Qt.Orientation.Horizontal)
            action = QAction(column_name, self, checkable=True)
            settings = QSettings("Parker Tonra", "Beat Bank")
            action.setChecked(not self.table.isColumnHidden(i))
            action.toggled.connect(lambda checked, index=i: self.toggle_column(checked, index))
            columns_menu.addAction(action)

    def toggle_column(self, checked, index):
        self.table.setColumnHidden(index, not checked)
        settings = QSettings("Parker Tonra", "Beat Bank")
        settings.setValue(f"columnVisibility/{index}", checked)

    def toggle_similar_tracks(self, checked):
        # Emit signal or perform action based on the state of the toggle
        if checked:
            # Emit signal or perform action to show similar tracks table
            pass
        else:
            # Emit signal or perform action to hide similar tracks table
            pass
    
    def toggle_reorder(self, checked):
        # Emit signal or perform action based on the state of the toggle
        if checked:
            # Emit signal or perform action to allow reordering
            pass
        else:
            # Emit signal or perform action to disallow reordering
            pass

    def open_read_me(self):
        # Open the readme file
        pass
    
    # -------------------------------------------------------------------------
    # Context Menu
    # -------------------------------------------------------------------------
    def contextMenuEvent(self, event):
        context_menu = QMenu(self)
        open_file_action = context_menu.addAction("Open File Location")
        edit_track_action = context_menu.addAction("Edit Track")
        delete_track_action = context_menu.addAction("Delete Track")
        open_ableton_action = context_menu.addAction("Open in Ableton") #TODO
        add_to_set_action = context_menu.addAction("Add to Set") #TODO
        play_audio_action = context_menu.addAction("Play Audio") #TODO
        action = context_menu.exec(event.globalPos())
        if action == open_file_action:
            self.open_file_location()
        elif action == edit_track_action:
            self.edit_track()
        elif action == delete_track_action:
            self.delete_track()
        elif action == open_ableton_action:
            pass
        elif action == add_to_set_action:
            pass
        elif action == play_audio_action:
            pass
    
    # -------------------------------------------------------------------------
    # Button linked functions
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
    
    def authenticate_user(self):
        if hasattr(self, 'gdrive_service'):
            print("User already authenticated.")
            return
        
        print("Authenticating user...")
        # Define the scopes your application requires
        SCOPES = ['https://www.googleapis.com/auth/drive']
        
        
        secret_path = os.path.join(os.path.dirname(__file__), '..','client_secrets.json')
        secret_path = os.path.abspath(secret_path)
        
        
        # Start the flow using the client secrets file you downloaded from the Google Developer Console
        flow = InstalledAppFlow.from_client_secrets_file(secret_path, SCOPES)
        
        # This will open the default web browser for the user to log in
        # After logging in, the user will be prompted to give your application access to their Google Drive
        auth_url, _ = flow.authorization_url(prompt='consent')
        
        webbrowser.open(auth_url)
        
        # Once authorized, exchange the authorization code for tokens
        flow.run_local_server(port=0)
        
        # Now you have credentials, you can create a service object to interact with the Drive API
        credentials = flow.credentials
        self.save_credentials(credentials)
        print("User authenticated. Saving credentials...")
        # Use these credentials to access Google Drive, for example
        self.gdrive_service = build('drive', 'v3', credentials=credentials)
        print("Service object created.")
    
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
    
    def open_file_location(self):
        current_row = self.table.currentIndex().row()
        if current_row < 0:
            self.show_warning_message("No Selection", "Please select a track to open its file location.")
            return

        file_path = self.model.record(current_row).value("file_path")
        print(f"Opening file location for {file_path}")
        if not os.path.exists(file_path):
            self.show_warning_message("File Not Found", "The file path does not exist.")
            return

        if platform.system() == 'Windows':
            print("Windows OS detected. Opening file location...")
            subprocess.Popen(f'explorer /select,"{file_path}"', shell=True)
        elif platform.system() == 'Darwin':  # macOS
            print("macOS detected. Opening file location...")
            subprocess.Popen(['open', '-R', file_path])
        else:  # Assuming Linux or other Unix-like OS
            print("Linux or Unix-like OS detected. Opening file location...")
            subprocess.Popen(['xdg-open', file_path])
        
    
    # -------------------------------------------------------------------------
    # Database operations
    # -------------------------------------------------------------------------
    def delete_from_database(self, track_id):
        query = QSqlQuery()
        query.prepare("DELETE FROM tracks WHERE id = :id")
        query.bindValue(":id", track_id)
        if query.exec():
            print("Track deleted successfully.")
            self.table_refresh()
        else:
            print("Failed to delete track:", query.lastError().text())

    # Utility functions
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
    
    def table_refresh(self):
        print("Refreshing table...")
        # Refresh the table
        self.model.select()
        pass
    
    def restore_table_state(self):
        print("Restoring table state...")
        settings = QSettings("Parker Tonra", "Beat Bank")
        state = settings.value("tableState")
        if state:
            print(f"State found. Restoring table state...")
            self.table.horizontalHeader().restoreState(state)
            for i in range(self.table.model().columnCount()):
                visible = settings.value(f"columnVisibility/{i}", True, type=bool)
                self.table.setColumnHidden(i, not visible)
        else:
            print("No state found.")   
       
    def closeEvent(self, event):
        print("Shutting down...")
        settings = QSettings("Parker Tonra", "Beat Bank")
        settings.setValue("tableState", self.table.horizontalHeader().saveState())
        super().closeEvent(event)
        
    def ask_user(self, title, message):
        dialog = AskUserDialog(title, message)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            return dialog.user_input
        return None
    
    # Function to save credentials to a file
    def save_credentials(self, credentials):
        with open('token.pickle', 'wb') as token:
            pickle.dump(credentials, token)
    
    # Function to load credentials from a file
    def load_credentials(self):
        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token:
                return pickle.load(token)
        return None
    # Google Drive Integration
    # -------------------------------------------------------------------------
    
    # function to find or create a folder in google drive
    def find_or_create_beatbank_folder(self):
        if not hasattr(self, 'gdrive_service'):
            print("User not authenticated.")
            return
        service = self.gdrive_service
        # Search for the folder by name
        folder_name = self.ask_user("Beat Bank folder", "Enter the name of the folder to store your Beat Bank files.")
        if folder_name:
            print(f"Folder: {folder_name}")
        else:
            print("No answer was entered or dialog was canceled.")
            return
        query = f"mimeType='application/vnd.google-apps.folder' and name='{folder_name}' and trashed=false"
        response = service.files().list(q=query,
                                        spaces='drive',
                                        fields='files(id, name)').execute()
        
        folders = response.get('files', [])

        # If the folder exists, return its ID
        if folders:
            return folders[0]['id']  # Assuming the first match is the one you want

        # If the folder doesn't exist, create it
        folder_metadata = {
            'name': folder_name,
            'mimeType': 'application/vnd.google-apps.folder'
        }
        folder = service.files().create(body=folder_metadata, fields='id').execute()
        return folder.get('id')
    
    def list_and_choose_folder(self):
        if not hasattr(self, 'gdrive_service'):
            print("User not authenticated.")
            return

        service = self.gdrive_service
        # Query to list folders
        query = "mimeType='application/vnd.google-apps.folder' and trashed=false"
        response = service.files().list(q=query,
                                        spaces='drive',
                                        fields='files(id, name)',
                                        pageSize=100).execute()  # Adjust pageSize as needed
        
        folders = response.get('files', [])

        # Check if there are folders
        if not folders:
            print("No folders found.")
            return

        # Create a dialog or use a custom method to display folders and let the user choose
        folder_names = [folder['name'] for folder in folders]
        folder_id, ok = self.show_folder_selection_dialog(folder_names)

        if ok and folder_id:
            # User made a selection, return the selected folder's ID
            selected_folder_name = folder_names[folder_id]
            for folder in folders:
                if folder['name'] == selected_folder_name:
                    return folder['id']
        else:
            print("No folder was selected or dialog was canceled.")
            return

    def show_folder_selection_dialog(self, folder_names):
        dialog = QInputDialog(self)
        dialog.setWindowTitle("Choose Folder")
        dialog.setLabelText("Select the folder to store your Beat Bank files:")
        dialog.setComboBoxItems(folder_names)
        dialog.setComboBoxEditable(False)
        ok = dialog.exec()
        return dialog.comboBoxItems().index(dialog.textValue()), ok
        
    def print_service_object(self):
        if hasattr(self, 'gdrive_service'):
            print(self.gdrive_service)
        else:
            print("User not authenticated.")
        return
     
    def check_song_file_integrity(self):
        invalid_rows = []
        query = QSqlQuery("SELECT id, file_path FROM tracks")  # Adjust SQL query as needed

        row = 0
        if query.exec():
            while query.next():
                file_path = query.value(1)  # Assuming file_path is the second column

                if not os.path.exists(file_path):
                    invalid_rows.append(row)
                row += 1
        else:
            print(f"Failed to execute query: {query.lastError().text()}")

        # Update the delegate with the invalid rows
        if invalid_rows:
            self.delegate.set_invalid_rows(invalid_rows)
            self.report_invalid_files(invalid_rows)
        else:
            print("All song file paths are valid.")

    def report_invalid_files(self, invalid_files):
        # Here you can implement how you want to report the invalid files to the user
        # For example, showing a dialog with a list of invalid file paths and options to remove or update them
        message = "The following files have invalid paths:\n" + "\n".join(f"ID: {song_id}, Path: {path}" for song_id, path in invalid_files)
        QMessageBox.information(self, "Invalid File Paths", message)
        
class AskUserDialog(QDialog):
    def __init__(self, title, message):
        super().__init__()
        self.setWindowTitle(title)
        self.setGeometry(100, 100, 300, 100)

        # Layout
        layout = QVBoxLayout()

        # Label
        self.label = QLabel(message)
        layout.addWidget(self.label)

        # Text Edit
        self.lineEdit = QLineEdit()
        layout.addWidget(self.lineEdit)

        # Button
        self.button = QPushButton("OK")
        self.button.clicked.connect(self.on_ok_clicked)
        layout.addWidget(self.button)

        self.setLayout(layout)
    
    def on_ok_clicked(self):
        self.user_input = self.lineEdit.text()
        self.accept()  # Closes the dialog and sets result to Accepted

class BeatTable(QTableView):
    trackDropped = pyqtSignal(str)
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.lastClickTime = QTime()
        self.doubleClickInterval = QtWidgets.QApplication.doubleClickInterval()
        self.setAcceptDrops(True)
        self.setDragEnabled(True)
        self.setMinimumHeight(500)
        self.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        self.horizontalHeader().setSectionsMovable(True)

    
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

class InvalidFileDelegate(QStyledItemDelegate):
    def __init__(self, parent=None):
        super().__init__(parent)
        # A set to keep track of rows that have invalid file paths
        self.invalid_rows = set()

    def paint(self, painter, option, index):
        if index.row() in self.invalid_rows:
            option.backgroundBrush = QBrush(QColor(255, 200, 200))  # Light red
        super().paint(painter, option, index)

    def set_invalid_rows(self, rows):
        self.invalid_rows = set(rows)
        self.parent().viewport().update()  # Update the view to reflect changes