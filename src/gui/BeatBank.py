# BeatBank.py (root)/src/gui/BeatBank.py
import os
import sys
import logging

from PyQt6.QtSql import QSqlQuery
from PyQt6.QtWidgets import (
    QMainWindow,
    QVBoxLayout,
    QWidget,
    QFileDialog,
    QMessageBox,
    QHBoxLayout,
    QHeaderView,
    QAbstractItemView,
    QMenu,
    QSplitter
)
from PyQt6.QtCore import QSettings

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
from src.styles.stylesheet_loader import StylesheetLoader

logger = logging.getLogger(__name__)


class MainWindow(QMainWindow):
    def __init__(self, db):
        # Initialization and basic setup
        super().__init__()
        self.init_ui(db)

    def init_ui(self, db):
        self.init_attributes(db)
        self.setupWindow()
        self.init_side_bar()
        self.init_filteredTableView()
        self.init_beat_table()
        self.init_setupLayouts()
        self.restore_table_state()
        self.restore_reorder_state()
        self.restore_edit_state()

        self.init_menu_bar()
        self.finalizeLayout()

    def init_attributes(self, db):
        # self.google_drive = GoogleDriveIntegration()
        self.audio_signal = PlayAudioSignal()
        self.audio_player = AudioPlayer(main_window=self)
        self.beat_jockey = BeatJockey(
            main_window=self, audio_player=self.audio_player)
        self.model_manager = ModelManager(database=db, main_window=self)
        self.model_manager.setup_models()
        self.proxy = self.model_manager.proxyModel

        self.selected_beat = None
        self.playing_beat = None

    def setupWindow(self):
        self.setWindowTitle('Beat Bank')
        self.setGeometry(100, 100, 1600, 200)

        self.style_sheet = StylesheetLoader.load_stylesheet('styles')
        self.setStyleSheet(self.style_sheet)
        self.declare_layouts()

    def declare_layouts(self):
        print("Creating layouts...")
        self.beatbank_splitter = QSplitter()  # TODO: Splitter for sidebar and main
        self.beatbank_layout = QHBoxLayout()
        self.main_layout = QVBoxLayout()
        self.table_layout = QHBoxLayout()
        self.bottom_layout = QHBoxLayout()

    def init_side_bar(self):
        print("creating sidebar...")
        self.sidebar = SideBar(self)
        self.setStyleSheet(self.style_sheet)
        self.sidebar_layout = self.sidebar.sidebar_layout

    def init_setupLayouts(self):
        print("Setting up layouts...")

        # Add widgets to layouts
        self.table_layout.addWidget(self.table)
        self.bottom_layout.addWidget(self.audio_player)

        # Add layouts to the main layout
        self.main_layout.addLayout(self.table_layout, 80)
        self.main_layout.addLayout(self.bottom_layout, 20)

        # Add sidebar_layout and main_layout to the splitter
        sidebar_widget = QWidget()
        sidebar_widget.setLayout(self.sidebar_layout)
        main_widget = QWidget()
        main_widget.setLayout(self.main_layout)

        self.beatbank_splitter.addWidget(sidebar_widget)
        self.beatbank_splitter.addWidget(main_widget)

        self.beatbank_splitter.setStretchFactor(0, 1)
        self.beatbank_splitter.setStretchFactor(1, 4)

        # Add the splitter to the main layout
        self.beatbank_layout.addWidget(self.beatbank_splitter)

        # Set the main widget and layout
        main_container = QWidget()
        main_container.setLayout(self.beatbank_layout)
        self.setCentralWidget(main_container)

        print("Layouts initialized.")

    def finalizeLayout(self):
        self.container = QWidget(self)
        self.container.setLayout(self.beatbank_layout)
        self.setCentralWidget(self.container)

    def get_selected_beat_path(self):
        if self.table.selected_beat:
            return self.selected_beat.get("File Location")
        print("No beat selected.")
        return None

    def get_selected_beat_id(self):
        if self.table.selected_beat:
            return self.table.selected_beat.get("Beat ID")
        print("No beat selected.")
        return None

    def init_beat_table(self):
        self.table = BeatTable(main_window=self,
                               beat_jockey=self.beat_jockey,
                               model=self.model_manager.model,
                               proxy=self.proxy,
                               model_manager=self.model_manager)
        self.delegate = InvalidFileDelegate(self.table)

        self.table.setSortingEnabled(True)
        self.table.verticalHeader().hide()
        self.table.resizeColumnsToContents()
        header = self.table.horizontalHeader()
        # Set all columns to stretch
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        # Make the last column fill the extra space
        header.setStretchLastSection(True)

        self.table.setStyleSheet(self.style_sheet)

        self.table.setShowGrid(False)
        self.table.setAlternatingRowColors(True)
        self.table.verticalHeader().setStyleSheet(self.style_sheet)
        self.table.horizontalHeader().setStyleSheet(self.style_sheet)
        self.table.setDragDropMode(QAbstractItemView.DragDropMode.InternalMove)

    def init_filteredTableView(self):
        self.filteredTableView = self.model_manager.proxyModel

    def init_menu_bar(self):
        menubar = InitializeMenuBar(main_window=self,
                                    menu_bar=self.menuBar(),
                                    table=self.table,
                                    model=self.model_manager.model
                                    )

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
                path, _ = QFileDialog.getOpenFileName(
                    self, "Select Audio File", "", "Audio Files (*.mp3 *.wav *.flac);;All Files (*)")
                if not path:
                    raise FileNotFoundError("No file selected.")
            added = self.model_manager.add_track_to_database(path)
            if not added:
                raise Exception("Database insertion failed.")
            self.table_refresh()
            print(f"Added track {path} to database.")
        except FileNotFoundError as e:
            logging.error(f"FileNotFoundError: {e}")
        except Exception as e:
            logging.error(f"General Exception: {e}")

    def edit_beat(self):
        track_id = self.table.selected_beat.get("Beat ID")
        print(f"Editing track...{track_id}")
        print(f"track id being edited: {track_id}")
        self.editWindow = EditTrackWindow(track_id)
        self.editWindow.trackEdited.connect(self.table_refresh)
        self.editWindow.show()

    def delete_beat(self):
        selected_row = self.table.currentIndex().row()
        id = self.model_manager.get_id_for_row(selected_row)
        self.model_manager.delete_beat_from_database(id)

    def update_selected_item(self):
        print("new item selected")
        current = self.table.currentIndex()
        self.update_selected_beat(current)

    def update_selected_beat(self):
        """
        Update the selected beat information based on the current selection.
        """
        current = self.selection_model.currentIndex()
        if not current.isValid():
            self.selected_beat = None
            print("No beat selected.")
            return

        # Assuming `current` is a QModelIndex, map it if using a proxy model
        if hasattr(self, 'model_manager') and self.proxy:
            try:
                current = self.selection_model.currentIndex()
                row = current.row()
                if row == -1:
                    raise IndexError("Invalid row index from proxy mapping.")
                row_data = self.model_manager.get_data_for_row(row)
                self.selected_beat = row_data
            except Exception as e:
                print(f"Error mapping index: {e}")
                return
        else:
            print("Model manager not defined or missing proxy model.")
            return

    def open_file_location(self):
        path = self.table.selected_beat.get("File Location")
        Utils.open_file_location(path)

    def check_song_file_integrity(self):
        invalid_files = []  # Store tuples of (song_id, file_path)
        # Adjust SQL query as needed
        query = QSqlQuery("SELECT id, file_path FROM tracks")

        if query.exec():
            while query.next():
                # Assuming song_id is the first column
                song_id = query.value(0)
                # Assuming file_path is the second column
                file_path = query.value(1)

                if not os.path.exists(file_path):
                    # Append tuple of song_id and file_path
                    invalid_files.append((song_id, file_path))

        else:
            print(f"Failed to execute query: {query.lastError().text()}")

        # Update the delegate with the invalid files, if necessary
        if invalid_files:
            # Assuming you update your delegate to handle a list of (song_id, file_path) tuples
            self.delegate.set_invalid_rows(invalid_files)
            self.report_invalid_files(invalid_files)
        else:
            print("All song file paths are valid.")

    # Utility
    def load_set(self, set_name):
        set_id = self.model_manager.get_set_id(set_name)
        print(f"Loading set: {set_name} with ID: {set_id}")

        if set_id:
            track_ids = self.model_manager.get_track_ids_for_set(set_id)
            
            if track_ids:
                # Build the query to fetch tracks
                query_string = "SELECT * FROM tracks WHERE id IN (" + ",".join([str(track_id) for track_id in track_ids]) + ")"
                query = QSqlQuery()
                query.prepare(query_string)
                
                if query.exec():
                    # Set the executed query to the model
                    self.model_manager.model.setQuery(query)
                    
                    # Optional: print out the results
                    while query.next():
                        print(f"Track ID: {query.value(0)}")
                else:
                    print("Failed to execute the query.")
            else:
                print("No track IDs found for the given set.")
        else:
            print("Invalid set name or set ID not found.")
                        

    def load_all_tracks(self):
        print("Loading all tracks...")
        self.model_manager.model.setQuery("SELECT * FROM tracks")
    
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
            print(self.table.model)
            for i in range(self.model_manager.model.columnCount()):
                visible = settings.value(
                    f"columnVisibility/{i}", True, type=bool)
                self.table.setColumnHidden(i, not visible)
        else:
            print("No state found.")

    def restore_reorder_state(self):
        settings = QSettings("Parker Tonra", "Beat Bank")
        reorder_allowed = settings.value("reorderState", True, type=bool)
        self.table.horizontalHeader().setSectionsMovable(reorder_allowed)
        print(
            f"Reorder state restored: {'Enabled' if reorder_allowed else 'Disabled'}")

    def restore_edit_state(self):
        settings = QSettings("Parker Tonra", "Beat Bank")
        edit_allowed = settings.value("editState", False, type=bool)
        self.table.setEditTriggers(
            QAbstractItemView.EditTrigger.DoubleClicked if edit_allowed else QAbstractItemView.EditTrigger.NoEditTriggers)
        print(
            f"Edit state restored: {'Enabled' if edit_allowed else 'Disabled'}")

    def save_as_default(self):
        settings = QSettings("Parker Tonra", "Beat Bank")
        settings.setValue("defaultTableState",
                          self.table.horizontalHeader().saveState())

    def load_default(self):
        settings = QSettings("Parker Tonra", "Beat Bank")
        state = settings.value("tableState")
        if state:
            print(f"State found. Restoring table state...")
            self.table.horizontalHeader().restoreState(state)
            for i in range(self.table.model().columnCount()):
                visible = settings.value(
                    f"columnVisibility/{i}", True, type=bool)
                self.table.setColumnHidden(i, not visible)

    def report_invalid_files(self, invalid_files):
        # Here you can implement how you want to report the invalid files to the user
        # For example, showing a dialog with a list of invalid file paths and options to remove or update them
        message = "The following files have invalid paths:\n" + \
            "\n".join(f"ID: {song_id}, Path: {path}" for song_id,
                      path in invalid_files)
        QMessageBox.information(self, "Invalid File Paths", message)

    # Event Overrides

    def closeEvent(self, event):
        print("Shutting down...")
        print("Saving table state..")
        settings = QSettings("Parker Tonra", "Beat Bank")
        settings.setValue(
            "tableState", self.table.horizontalHeader().saveState())
        super().closeEvent(event)

    def toggle_click_edit(self, allow_edit):
        # Set the editability of the table or other components as needed
        self.table.setEditTriggers(
            QAbstractItemView.EditTrigger.DoubleClicked if allow_edit else QAbstractItemView.EditTrigger.NoEditTriggers)
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
        if self.sidebar_layout.geometry().contains(event.pos()):
            self.sidebar_context_menu(event)
        elif self.table.geometry().contains(event.pos()):
            self.table_context_menu(event)
        else:
            self.default_context_menu(event)

    def table_context_menu(self, event):
        context_menu = QMenu(self)
        user_sets = self.get_user_sets()
        add_to_set_menu = context_menu.addMenu("Add to Set")
        current_track_id = self.get_selected_beat_id()
        print(f"Current track ID: {current_track_id}")
        for set_name in user_sets:
            set_action = add_to_set_menu.addAction(set_name)
            set_action.setCheckable(True)
            if self.is_track_in_set(current_track_id, set_name):
                set_action.setChecked(True)
            set_action.triggered.connect(lambda checked, set_name=set_name: self.toggle_track_in_set(
                current_track_id, set_name, checked))
        open_file_action = context_menu.addAction("Open File Location")
        edit_beat_action = context_menu.addAction("Edit Beat")
        delete_beat_action = context_menu.addAction("Delete Beat")
        open_ableton_action = context_menu.addAction("Open in Ableton")  # TODO
        add_to_set_action = context_menu.addAction("Add to Set")  # TODO
        play_audio_action = context_menu.addAction("Play Audio")  # TODO
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

    def is_track_in_set(self, track_id, set_name):
        self.model_manager.is_track_in_set(track_id, set_name)

    def toggle_track_in_set(self, track_id, set_name, checked):
        self.model_manager.toggle_track_in_set(track_id, set_name, checked)

    def sidebar_context_menu(self, event):
        context_menu = QMenu(self)
        foo_bar = context_menu.addAction("foo")
        action = context_menu.exec(event.globalPos())
        if action == foo_bar:
            print("foo")

    def default_context_menu(self, event):
        pass

    def add_to_set(self, set_name):
        # Logic for adding to the set
        print(f"Adding to set: {set_name}")
        # Implement the actual functionality here

    def get_user_sets(self):
        sets = []
        query = QSqlQuery("SELECT name FROM user_sets")
        while query.next():
            sets.append(query.value(0))
        return sets

    # TODO
    def open_read_me(self):
        # Open the readme file TODO
        pass

    def debug_print(self):
        print(f"drag mode on table: {self.table.dragDropMode()}")
        print(f"drop action on table: {self.table.acceptDrops()}")
        # print if the table is editable
        
