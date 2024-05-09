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
        self.setGeometry(100, 100, 1400, 200)

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

        self.table_layout.addWidget(self.table)

        self.bottom_layout.addWidget(self.audio_player)

        # Add table and bottom to main layout
        self.main_layout.addWidget(self.table, 80)
        self.main_layout.addLayout(self.bottom_layout, 20)

        # sidebar takes up 10% of space
        self.beatbank_layout.addLayout(self.sidebar_layout, 10)
        # main takes up 90% of space
        self.beatbank_layout.addLayout(self.main_layout, 90)

        print("Layouts initialized.")

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
        # header.setStretchLastSection(True)  # Make the last column fill the extra space

        self.table.setStyleSheet("""
        QTableView 
        {
            border: 1px solid #444;
            border-radius: 5px;
            background-color: #222;
            color: #EEE;
            font-size: 24px;
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

        self.table.setShowGrid(False)
        
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
        print("Editing track...")
        selected_row = self.table.currentIndex().row()
        if selected_row < 0:
            # set the font color to gray and say "no track playing"
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

    def update_selected_item(self):
        print("new item selected")
        current = self.table.currentIndex()
        self.update_selected_beat(current)

    def update_selected_beat(self):
        """
        Update the selected beat information based on the current selection.
        """
        current = self.selection_model.currentIndex()
        print(f"Current index: {current}")
        print(f"Current index data: {current.data()}")

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
                print(f"Row: {row}")
                row_data = self.model_manager.get_data_for_row(row)
                self.selected_beat = row_data
                print(f"Selected beat updated: {self.selected_beat}")
            except Exception as e:
                print(f"Error mapping index: {e}")
                self.selected_beat = {
                    'Row Number': 0,
                    'Beat ID': '',
                    'Title': '',
                    'Length': '',
                    'Key': '',
                    'Date Created': '',
                    'Date Added': '',
                    'Notes': '',
                    'File Location': '',
                    'Ableton File Location': '',
                    'Artist': 0,
                    'Current Version ID': 0.0,
                    'Tempo': None
                }
        else:
            print("Model manager not defined or missing proxy model.")
            self.selected_beat = {
                'Row Number': 0,
                'Beat ID': '',
                'Title': '',
                'Length': '',
                'Key': '',
                'Date Created': '',
                'Date Added': '',
                'Notes': '',
                'File Location': '',
                'Ableton File Location': '',
                'Artist': 0,
                'Current Version ID': 0.0,
                'Tempo': None
            }
        
        # if hasattr(self, 'model_manager') and self.model_manager.model:
        #     proxy_row = current.row()
        #     beat_id = self.model_manager.get_id_for_row(proxy_row)
        #     query = QSqlQuery()
        #     # query for the item with id 'beat_id'
        #     query.exec(f"SELECT * FROM tracks WHERE id = {beat_id}")
        #     if query.next():
        #         self.selected_beat = query.record()
        #         print(
        #             f"Selected track updated: {self.selected_beat.value('file_path')}")
        #     path = self.selected_beat.value('file_path')
        #     beatLength = self.selected_beat.value('length')
        #     if not beatLength:
        #         beatLength = '0:00'
        #     print(f"path: {path}")
        #     print(f"length: {beatLength}")
        #     self.beat_jockey.update_current_song(path, beatLength)

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

    def open_file_location(self):
        current_row = self.table.currentIndex().row()
        if current_row < 0:
            Utils.show_warning_message(
                "No Selection", "Please select a track to open its file location.")
            return

        file_path = self.model_manager.get_file_path_for_row(current_row)
        print(f"Opening file location: {file_path}")
        Utils.open_file_location(file_path)

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
        context_menu = QMenu(self)
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

    # TODO
    def open_read_me(self):
        # Open the readme file TODO
        pass

    def debug_print(self):
        logger.info("Debugging...")
        logger.info("Selected track:", self.selected_beat)
        logger.info("Playing track:", self.playing_beat)
