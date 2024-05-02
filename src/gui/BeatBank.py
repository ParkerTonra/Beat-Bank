#BeatBank.py (root)/src/gui/BeatBank.py
import os, sys

from PyQt6.QtSql import QSqlTableModel, QSqlQuery
from PyQt6.QtWidgets import (
    QMainWindow,
    QVBoxLayout,
    QWidget,
    QFileDialog,
    QMessageBox,
    QHBoxLayout,
    QFrame,
    QTableView,
    QMenu,
    QDialog,
    QSplitter,
    QHeaderView
)
from PyQt6.QtCore import QSettings, Qt


from controllers.database_controller import DatabaseController
from gui import play_audio
from gui.BeatTable import BeatTable
from gui.signals import PlayAudioSignal
from gui.edit_track_window import EditTrackWindow
from gui.ask_user import AskUserDialog
from gui.menu_bar import InitializeMenuBar
from gui.side_bar import SideBar
from gui.InvalidFileDelegate import InvalidFileDelegate
from gui.model_manager import ModelManager

from controllers.gdrive_integration import GoogleDriveIntegration
from utilities.utils import Utils

class MainWindow(QMainWindow):
    def __init__(self, db):
        # Initialization and basic setup
        super().__init__()
        self.controller = DatabaseController(db)
        self.google_drive = GoogleDriveIntegration()
        self._updating_cell = False
        self.isEditing = False
        self.audio_signal = PlayAudioSignal()
        self.audio_signal.playAudioSignal.connect(self.model_play_audio)
        self.audio_player = play_audio.AudioPlayer()
        
        
        
        #flags to universally know what is selected and playing
        self.selected_beat = None
        self.playing_beat = None
        
        # Initialize the model manager
        self.model_manager = ModelManager(db, self)
        self.model_manager.setup_models()
        
        self.init_ui()
        selection_model = self.table.selectionModel()
        selection_model.currentRowChanged.connect(self.update_selected_beat)
        self.bottom_layout.addWidget(self.audio_player)
        self.table.trackDropped.connect(self.add_track)
        self.editWindow = None

    # UI Setup
    def init_ui(self):
        self.setupWindow()
        self.init_side_bar()
        self.init_beat_table()
        self.declare_layouts()
        self.init_setupLayouts()
        self.restore_table_state()
        self.restore_reorder_state()
        self.init_filteredTableView()
        self.init_menu_bar()
        self.finalizeLayout()

    def setupWindow(self):
        self.setWindowTitle('Beat Bank')
        self.setGeometry(100, 100, 1400, 200)

    

    def declare_layouts(self):
        print("Creating layouts...")
        self.beatbank_splitter = QSplitter() #Splitter for sidebar and main
        self.beatbank_layout = QHBoxLayout() 
        self.main_layout = QVBoxLayout()
        self.table_layout = QVBoxLayout()
        self.bottom_layout = QHBoxLayout()

    def init_side_bar(self):
            print("creating sidebar...")
            self.sidebar = SideBar(self)
            self.setStyleSheet("""
                QListView {
                    background-color: #222; /* Dark background */
                    color: #EEE; /* Light text color */
                    font: 16px; /* Font size */
                    border: none; /* No border around the view */
                }
                QListView::item {
                    border: 1px solid #FFFFFF; /* Subtle border for each item */
                    border-radius: 6px; /* Slightly rounded corners for the border */
                    margin: 2px; /* Margin around items */
                    padding: 5px; /* Padding inside items */
                }
                QListView::item:selected {
                    background-color: #666; /* Background color of a selected item */
                }
                QListView::item:hover {
                    background-color: #555; /* Background color when hovering over an item */
                }
                """)
            self.sidebar_layout = self.sidebar.sidebar_layout
    
    def init_setupLayouts(self):
        print("Setting up layouts...")
        self.table_layout.addWidget(self.table)
        
        # Add table and bottom to main layout
        self.main_layout.addLayout(self.table_layout, 80)
        self.main_layout.addLayout(self.bottom_layout, 20)
        
        self.beatbank_layout.addLayout(self.sidebar_layout, 10) # sidebar takes up 10% of space
        self.beatbank_layout.addLayout(self.main_layout, 90) # main takes up 90% of space
        
        
        
        print("Layouts initialized.")
        
        #TODO: sidebar

    def finalizeLayout(self):
        self.container = QWidget(self)
        self.container.setLayout(self.beatbank_layout)
        self.setCentralWidget(self.container)
        

    def init_beat_table(self):
        self.table = BeatTable(self, self.audio_signal)
        self.delegate = InvalidFileDelegate(self.table)
        self.table.setItemDelegate(self.delegate)
        self.table.setModel(self.model_manager.proxyModel)
        self.table.setSortingEnabled(True)
        self.table.verticalHeader().hide()
        self.table.setStyleSheet("""
        QTableView {
            border: 1px solid #444;
            border-radius: 5px;
            background-color: #222;
            color: #EEE;
        }
        QHeaderView::section {
            background-color: #333;
            padding: 5px;
            border: 1px solid #444;
            font-size: 14px;
            color: #FFF;
        }
        QTableView QTableCornerButton::section {
            background: #333;
            border: 1px solid #444;
        }
        """)
        

    def init_filteredTableView(self):
        self.filteredTableView = QTableView(self)
        self.filteredTableView.setFrameStyle(QFrame.Shape.Panel | QFrame.Shadow.Sunken)

    def init_menu_bar(self):
        menubar = InitializeMenuBar(self)
        menubar.init_menu_bar()
    
    # Event Handlers and Slots
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

    def model_play_audio(self):
        print("Playing audio... pt2")
        self.selected_beat
        
        
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
        
    def edit_beat(self):
        print("Editing track...")
        selected_row = self.table.currentIndex().row()
        if selected_row < 0:
            #set the font color to gray and say "no track playing"
            print("No track selected for editing.")
            return
        track_id = self.model_manager.get_id_for_row(selected_row)
        self.editWindow = EditTrackWindow(track_id)
        self.editWindow.trackEdited.connect(self.table_refresh)
        self.editWindow.show()
    
    def delete_beat(self):
        selected_row = self.table.currentIndex().row()
        self.controller.controller_delete_beat(selected_row)
    
    def add_playlist(self):
        print("Adding playlist...")
        # Add playlist logic here
        pass
    #remove_playlist
    #open_settings
    #refresh_list
    def remove_playlist(self):
        print("Removing playlist...")
        # Remove playlist logic here
        pass
    
    def open_settings(self):
        print("Opening settings...")
        # Open settings dialog or window
        pass
    
    def show_similar_tracks(self):
        # Show similar tracks logic here
        pass
    
    # Database Operations
    def delete_from_database(self, track_id):
        query = QSqlQuery()
        query.prepare("DELETE FROM tracks WHERE id = :id")
        query.bindValue(":id", track_id)
        if query.exec():
            print("Track deleted successfully.")
            self.table_refresh()
        else:
            print("Failed to delete track:", query.lastError().text())
    
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

    def debug_print(self):
        print("Debugging...")
        print("Selected track:", self.selected_beat)
        print("Playing track:", self.playing_beat)
    
    def update_selected_beat(self, current, previous):
        """
        Update the selected beat information based on the current selection.
        """
        if not current.isValid():
            self.selected_beat = None
            print("No beat selected.")
            return

        # Assuming `current` is a QModelIndex, map it if using a proxy model
        if hasattr(self, 'model_manager') and self.model_manager.proxyModel:
            source_index = self.model_manager.proxyModel.mapToSource(current)
            row_data = {self.model_manager.model.headerData(i, Qt.Orientation.Horizontal): self.model_manager.model.record(source_index.row()).value(i) for i in range(self.model_manager.model.columnCount())}
            self.selected_beat = row_data
            print(f"Selected track updated: {self.selected_beat}")
        else:
            print("Model manager not defined or missing proxy model.")
        
    
    # Utility
    def table_refresh(self):
        self.model_manager.refresh_model()
    
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
    
    def restore_reorder_state(self):
        settings = QSettings("Parker Tonra", "Beat Bank")
        # Default to True if the setting has never been set
        reorder_allowed = settings.value("reorderState", True, type=bool)
        self.table.horizontalHeader().setSectionsMovable(reorder_allowed)
        print(f"Reorder state restored: {'Enabled' if reorder_allowed else 'Disabled'}")
    
    
    def ask_user(self, title, message):
        dialog = AskUserDialog(title, message)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            return dialog.user_input
        return None
    
    def open_file_location(self):
        current_row = self.table.currentIndex().row()
        if current_row < 0:
            Utils.show_warning_message("No Selection", "Please select a track to open its file location.")
            return

        file_path = self.model.record(current_row).value("file_path")
        print(f"Opening file location: {file_path}")
        Utils.open_file_location(file_path)
    
    def save_as_default(self):
            settings = QSettings("Parker Tonra", "Beat Bank")
            settings.setValue("defaultTableState", self.table.horizontalHeader().saveState())
            
    def load_default(self):
        settings = QSettings("Parker Tonra", "Beat Bank")
        state = settings.value("tableState")
        if state:
            print(f"State found. Restoring table state...")
            self.table.horizontalHeader().restoreState(state)
            for i in range(self.table.model().columnCount()):
                visible = settings.value(f"columnVisibility/{i}", True, type=bool)
                self.table.setColumnHidden(i, not visible)
            
    def report_invalid_files(self, invalid_files):
        # Here you can implement how you want to report the invalid files to the user
        # For example, showing a dialog with a list of invalid file paths and options to remove or update them
        message = "The following files have invalid paths:\n" + "\n".join(f"ID: {song_id}, Path: {path}" for song_id, path in invalid_files)
        QMessageBox.information(self, "Invalid File Paths", message)

    # Event Overrides
    def closeEvent(self, event):
        print("Shutting down...")
        print("Saving table state..")
        settings = QSettings("Parker Tonra", "Beat Bank")
        settings.setValue("tableState", self.table.horizontalHeader().saveState())
        super().closeEvent(event)
    
    def toggle_reorder(self, allow_reorder):
        # Set the movability of the table's column headers
        self.table.horizontalHeader().setSectionsMovable(allow_reorder)

        # Update the settings with the new reorder state
        settings = QSettings("Parker Tonra", "Beat Bank")
        settings.setValue("reorderState", allow_reorder)
        settings.sync()  # Ensure changes are immediately written to the persistent storage

        
    def action_triggered(self, checked):
        self.toggle_reorder(checked)        
    
    def contextMenuEvent(self, event):
        context_menu = QMenu(self)
        open_file_action = context_menu.addAction("Open File Location")
        edit_beat_action = context_menu.addAction("Edit Beat")
        delete_beat_action = context_menu.addAction("Delete Beat")
        open_ableton_action = context_menu.addAction("Open in Ableton") #TODO
        add_to_set_action = context_menu.addAction("Add to Set") #TODO
        play_audio_action = context_menu.addAction("Play Audio") #TODO
        action = context_menu.exec(event.globalPos())
        if action == open_file_action:
            self.open_file_location()
        elif action == edit_beat_action:
            self.edit_beat()
        elif action == delete_beat_action:
            self.delete_beat()
        elif action == open_ableton_action:
            pass
        elif action == add_to_set_action:
            pass
        elif action == play_audio_action:
            pass

    # TODO
    def open_read_me(self):
        # Open the readme file TODO
        pass
