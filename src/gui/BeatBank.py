#BeatBank.py (root)/src/gui/BeatBank.py
import os, sys

from PyQt6.QtSql import QSqlQuery
from PyQt6.QtWidgets import (
    QMainWindow,
    QVBoxLayout,
    QWidget,
    QFileDialog,
    QMessageBox,
    QHBoxLayout,
    QHeaderView,
    QFrame,
    QAbstractItemView,
    QMenu,
    QSplitter
)
from PyQt6.QtCore import QSettings, Qt

from src.gui.play_audio import AudioPlayer
from src.gui.BeatTable import BeatTable
from src.gui.signals import PlayAudioSignal
from src.gui.edit_track_window import EditTrackWindow
from src.gui.menu_bar import InitializeMenuBar
from src.gui.side_bar import SideBar
from src.gui.InvalidFileDelegate import InvalidFileDelegate
from src.gui.model_manager import ModelManager
from src.controllers.gdrive_integration import GoogleDriveIntegration
from src.utilities.utils import Utils
from src.gui.play_audio import BeatJockey

class MainWindow(QMainWindow):
    def __init__(self, db):
        # Initialization and basic setup
        super().__init__()

        self.google_drive = GoogleDriveIntegration()
        
        self.audio_signal = PlayAudioSignal()
        self.audio_player = AudioPlayer(self)
        self.beat_jockey = BeatJockey(main_window=self, audio_player=self.audio_player)
        self.model_manager = ModelManager(db, self)
        
        self.model_manager.setup_models()
        
        #flags to universally know what is selected and playing
        self.selected_beat = None
        self.playing_beat = None
        
        self.init_ui()
        selection_model = self.table.selectionModel()
        selection_model.currentRowChanged.connect(self.update_selected_beat)
        selection_model.selectionChanged.connect(self.update_selected_item)

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
        self.restore_edit_state()
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
        self.table_layout = QHBoxLayout()
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
        self.main_layout.addWidget(self.table, 80)
        self.main_layout.addLayout(self.bottom_layout, 20)
        
        self.beatbank_layout.addLayout(self.sidebar_layout, 10) # sidebar takes up 10% of space
        self.beatbank_layout.addLayout(self.main_layout, 90) # main takes up 90% of space
        
        
        
        print("Layouts initialized.")
        
        #TODO: sidebar

    def finalizeLayout(self):
        self.container = QWidget(self)
        self.container.setLayout(self.beatbank_layout)
        self.setCentralWidget(self.container)
        
    def get_selected_beat_path(self):
        if self.selected_beat:
            print("Selected new beat(BB)")
            return self.selected_beat.get("File Location")
        print("No beat selected.")
        return None
    
    def init_beat_table(self):
        self.table = BeatTable(parent = self, 
                               audio_signal = self.audio_signal,
                               beat_jockey = self.beat_jockey
                               )
        self.delegate = InvalidFileDelegate(self.table)
        self.table.setModel(self.model_manager.proxyModel)
        self.table.setSortingEnabled(True)
        self.table.verticalHeader().hide()
        self.table.resizeColumnsToContents()
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)  # Set all columns to stretch
        #header.setStretchLastSection(True)  # Make the last column fill the extra space
        
        self.table.setStyleSheet("""
        QTableView 
        {
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
        self.filteredTableView = self.model_manager.proxyModel

    def init_menu_bar(self):
        menubar = InitializeMenuBar(self)
        menubar.init_menu_bar()
    
    # Event Handlers and Slots
    def toggle_column(self, checked, index):
        self.table.setColumnHidden(index, not checked)
        settings = QSettings("Parker Tonra", "Beat Bank")
        settings.setValue(f"columnVisibility/{index}", checked)

    def toggle_similar_tracks(self, checked):
        # TODO: similar tracks.
        # Emit signal or perform action based on the state of the toggle
        if checked:
            # Emit signal or perform action to show similar tracks table
            pass
        else:
            # Emit signal or perform action to hide similar tracks table
            pass

        
    def get_selected_beat(self):
        return self.selected_beat    
    def add_track(self, path=None):
        try:
            if not path:
                path, _ = QFileDialog.getOpenFileName(self, "Select Audio File", "", "Audio Files (*.mp3 *.wav *.flac);;All Files (*)")
                if not path:
                    raise FileNotFoundError("No file selected.")
            added = self.model_manager.add_track_to_database(path)
            if not added:
                raise Exception("Database insertion failed.")
            self.table_refresh()
            print(f"Added track {path} to database.")
        except FileNotFoundError as e:
            print(e)
        except Exception as e:
            print(f"Failed to add track: {e}")
        
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
        id = self.model_manager.get_id_for_row(selected_row)
        self.model_manager.delete_beat_from_database(id)

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
    
    def update_selected_item(self):
        print("new item selected")
        current = self.table.currentIndex()
        self.update_selected_beat(current)
    
    def update_selected_beat(self, current):
        """
        Update the selected beat information based on the current selection.
        """
        print("Updating selected beat...")
        if not current.isValid():
            self.selected_beat = None
            print("No beat selected.")
            return

        # Assuming `current` is a QModelIndex, map it if using a proxy model
        if hasattr(self, 'model_manager') and self.model_manager.proxyModel:
            proxy_row = current.row()
            beat_id = self.model_manager.get_id_for_row(proxy_row)
            query = QSqlQuery()
            #query for the item with id 'beat_id'
            query.exec(f"SELECT * FROM tracks WHERE id = {beat_id}")
            if query.next():
                self.selected_beat = query.record()
                print(f"Selected track updated: {self.selected_beat.value('file_path')}")
            path = self.selected_beat.value('file_path')
            beatLength = self.selected_beat.value('length')
            if not beatLength:
                beatLength = '0:00'
            print(f"path: {path}")
            print(f"length: {beatLength}")
            self.beat_jockey.update_current_song(path, beatLength)

        
    
    
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
        reorder_allowed = settings.value("reorderState", True, type=bool)
        self.table.horizontalHeader().setSectionsMovable(reorder_allowed)
        print(f"Reorder state restored: {'Enabled' if reorder_allowed else 'Disabled'}")

    def restore_edit_state(self):
        settings = QSettings("Parker Tonra", "Beat Bank")
        edit_allowed = settings.value("editState", False, type=bool)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.DoubleClicked if edit_allowed else QAbstractItemView.EditTrigger.NoEditTriggers)
        print(f"Edit state restored: {'Enabled' if edit_allowed else 'Disabled'}")

    def open_file_location(self):
        current_row = self.table.currentIndex().row()
        if current_row < 0:
            Utils.show_warning_message("No Selection", "Please select a track to open its file location.")
            return

        file_path = self.model_manager.get_file_path_for_row(current_row)
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
    
    def toggle_click_edit(self, allow_edit):
        # Set the editability of the table or other components as needed
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.DoubleClicked if allow_edit else QAbstractItemView.EditTrigger.NoEditTriggers)
        # Update the settings with the new edit state
        settings = QSettings("Parker Tonra", "Beat Bank")
        settings.setValue("editState", allow_edit)
        settings.sync()  # Ensure changes are immediately written to the persistent storage
    
    def toggle_reorder(self, allow_reorder):
        # Set the movability of the table's column headers
        self.table.horizontalHeader().setSectionsMovable(allow_reorder)

        # Update the settings with the new reorder state
        settings = QSettings("Parker Tonra", "Beat Bank")
        settings.setValue("reorderState", allow_reorder)
        settings.sync()  # Ensure changes are immediately written to the persistent storage

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
