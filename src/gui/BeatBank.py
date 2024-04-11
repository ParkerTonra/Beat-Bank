#BeatBank.py (root)/src/gui/BeatBank.py
import os, sys

from PyQt6.QtSql import QSqlTableModel, QSqlQuery
from PyQt6.QtWidgets import (
    QMainWindow, QVBoxLayout, QWidget, QFileDialog, QMessageBox, QHBoxLayout, QFrame,
    QAbstractItemView, QTableView, QMenu, QDialog,QStyledItemDelegate
)
from PyQt6.QtCore import Qt, QSettings, QSortFilterProxyModel
from PyQt6.QtGui import QAction, QBrush, QColor

from utilities.util import Utils
from controllers.database_controller import DatabaseController
from gui import play_audio
from gui.BeatTable import BeatTable
from gui.signals import PlayAudioSignal
from gui.edit_track_window import EditTrackWindow
from gui.ask_user import AskUserDialog
from gui.menu_bar import InitializeMenuBar

from controllers.gdrive_integration import GoogleDriveIntegration
class MainWindow(QMainWindow):
    # -------------------------------------------------------------------------
    # Initialization / UI Setup
    # -------------------------------------------------------------------------
    def __init__(self, db):
        super().__init__()
        self.controller = DatabaseController(db)
        self.google_drive = GoogleDriveIntegration()
        self._updating_cell = False
        self.isEditing = False
        self.audio_signal = PlayAudioSignal()  # Make it an instance attribute
        self.audio_signal.playAudioSignal.connect(self.model_play_audio)
        self.audio_player = play_audio.AudioPlayer()
        self.init_ui()
        self.bottom_layout.addWidget(self.audio_player)
        self.table.trackDropped.connect(self.add_track)
        self.editWindow = None
        
    def model_play_audio(self):
        print("Playing audio... pt2")

        # Get the selection model from the table view
        selectionModel = self.table.selectionModel()

        # Check if there is any selection
        if selectionModel.hasSelection():
            # Get the indexes of the selected rows
            selectedIndexes = selectionModel.selectedRows()

            # Assuming you want to play the first selected item
            if selectedIndexes:
                firstSelectedIndex = selectedIndexes[0]
                current_row = firstSelectedIndex.row()
                path = self.model.record(current_row).value("file_path")
                track_title = self.model.record(current_row).value("title")

                # Update the audio player with the current track and play
                self.audio_player.update_current_track(track_title)
                self.audio_player.playAudio(path)
        else:
            print("No selection made.")
          

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

    # -------------------------------------------------------------------------
    # UI component initialization
    # -------------------------------------------------------------------------
    
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

    def init_setupLayouts(self):
        print("Setting up layouts...")
        self.main_layout = QVBoxLayout()
        
        # Create top and table layouts
        self.top_layout = QHBoxLayout()
        self.table_layout = QVBoxLayout()
        self.bottom_layout = QHBoxLayout()
        

        # Add top and table layouts to the main layout
        self.main_layout.addLayout(self.top_layout)
        self.main_layout.addLayout(self.table_layout)
        self.main_layout.addLayout(self.bottom_layout)

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
        self.table = BeatTable(self, self.audio_signal)
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
        print("Initializing (NEW) menu bar...")
        menubar = InitializeMenuBar(self)
        menubar.init_menu_bar()
        

    def init_columns_submenu(self, columns_menu):
        for i in range(self.table.model().columnCount()):
            column_name = self.table.model().headerData(i, Qt.Orientation.Horizontal)
            action = QAction(column_name, self, checkable=True)
            settings = QSettings("Parker Tonra", "Beat Bank")
            action.setChecked(not self.table.isColumnHidden(i))
            action.toggled.connect(lambda checked, index=i: self.toggle_column(checked, index))
            columns_menu.addAction(action)
    
    def init_toggles(self, toggle_click_edit):
        settings = QSettings("Parker Tonra", "Beat Bank")
        clickToEdit = settings.value("clickToEdit", type=bool)
        print(f"clickToEdit: {clickToEdit}")
        toggle_click_edit.setChecked(clickToEdit)
        if clickToEdit:
            self.table.setEditTriggers(QAbstractItemView.EditTrigger.DoubleClicked)
        else:
            self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
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

    def toggle_click_edit(self, checked):
        #toggle table editing. when checked, allow editing. When unchecked, disallow editing
        if checked:
            self.table.setEditTriggers(QAbstractItemView.EditTrigger.DoubleClicked)
        else:
            self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        settings = QSettings("Parker Tonra", "Beat Bank")
        print(f"saving clickToEdit as: {checked}")
        settings.setValue("clickToEdit", checked)

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
    # Database operations
    # -------------------------------------------------------------------------
    def add_track(self, path=None):
        if not path:
            path, _ = QFileDialog.getOpenFileName(self, "Select Audio File", "", "Audio Files (*.mp3 *.wav *.flac);;All Files (*)")
            if not path:
                #open file dialog to select file
                Utils.open_file_dialog()
        added = self.controller.controller_add_track(path)
        if added:
            self.table_refresh()
            print(f"Added track {path} to database.")
        else:
            print("Failed to add track.")
        

    def edit_track(self):
        print("Editing track...")
        selected_row = self.table.currentIndex().row()
        if selected_row < 0:
            #set the font color to gray and say "no track playing"
            print("No track selected for editing.")
            return
        track_id = self.model.record(selected_row).value("id")
        self.editWindow = EditTrackWindow(track_id)
        self.editWindow.trackEdited.connect(self.table_refresh)
        self.editWindow.show()
    
    def delete_track(self):
        selected_row = self.table.currentIndex().row()
        self.controller.controller_delete_track(selected_row)
        
    
    def delete_from_database(self, track_id):
        query = QSqlQuery()
        query.prepare("DELETE FROM tracks WHERE id = :id")
        query.bindValue(":id", track_id)
        if query.exec():
            print("Track deleted successfully.")
            self.table_refresh()
        else:
            print("Failed to delete track:", query.lastError().text())
    
    # -------------------------------------------------------------------------
    # Utility functions
    # -------------------------------------------------------------------------
    def table_refresh(self):
        print("Refreshing table...")
        # Refresh the table
        self.model.select()
        pass
    
    def handle_track_not_found(self, track_id):
        # Log the error, show a message box, or take other appropriate action
        print(f"Track with ID {track_id} not found.")

    def handle_update_error(self, exception):
        # Log the error, show a message box, or take other appropriate action
        print(f"An error occurred during table update: {exception}")
    
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
    
    def ask_user(self, title, message):
        dialog = AskUserDialog(title, message)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            return dialog.user_input
        return None
    
    def closeEvent(self, event):
        print("Shutting down...")
        settings = QSettings("Parker Tonra", "Beat Bank")
        settings.setValue("tableState", self.table.horizontalHeader().saveState())
        super().closeEvent(event)

    def open_file_location(self):
        current_row = self.table.currentIndex().row()
        if current_row < 0:
            Utils.show_warning_message("No Selection", "Please select a track to open its file location.")
            return

        file_path = self.model.record(current_row).value("file_path")
        print(f"Opening file location: {file_path}")
        Utils.open_file_location(file_path)
        
    def check_song_file_integrity(self):
        invalid_files = []  # Store tuples of (song_id, file_path)
        query = QSqlQuery("SELECT id, file_path FROM tracks")  # Adjust SQL query as needed

        if query.exec():
            while query.next():
                song_id = query.value(0)  # Assuming song_id is the first column
                file_path = query.value(1)  # Assuming file_path is the second column

                if not os.path.exists(file_path):
                    invalid_files.append((song_id, file_path))  # Append tuple of song_id and file_path

        else:
            print(f"Failed to execute query: {query.lastError().text()}")

        # Update the delegate with the invalid files, if necessary
        if invalid_files:
            # Assuming you update your delegate to handle a list of (song_id, file_path) tuples
            self.delegate.set_invalid_rows(invalid_files)
            self.report_invalid_files(invalid_files)
        else:
            print("All song file paths are valid.")

    def report_invalid_files(self, invalid_files):
        # Here you can implement how you want to report the invalid files to the user
        # For example, showing a dialog with a list of invalid file paths and options to remove or update them
        message = "The following files have invalid paths:\n" + "\n".join(f"ID: {song_id}, Path: {path}" for song_id, path in invalid_files)
        QMessageBox.information(self, "Invalid File Paths", message)
        
    # -------------------------------------------------------------------------
    # Google Drive Integration
    # -------------------------------------------------------------------------




#TODO: for checking integrity. looks if any file paths are invalid, paints the row red.
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

