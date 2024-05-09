from PyQt6.QtCore import QSettings, Qt
from PyQt6.QtGui import QAction
from src.utilities.utils import Utils
import sys

class InitializeMenuBar:
    # Init functions
    def __init__(self, main_window, menu_bar, table, model):
        self.main_window = main_window
        self.menu_bar = menu_bar
        self.table = table
        self.model = model
        self.init_menu_bar()

    def init_menu_bar(self):
        self.init_file_menu()
        self.init_edit_menu()
        self.init_view_menu()
        self.init_settings_menu()
        self.init_tools_menu()
        self.init_help_menu()
        
    def init_file_menu(self):
        file_menu = self.menu_bar.addMenu("&File")

        exit_action = QAction("&Exit", self.main_window)
        exit_action.triggered.connect(self.main_window.close)
        
        add_track_action = QAction("&Add Track", self.main_window)
        add_track_action.triggered.connect(self.main_window.add_track)
        
        refresh_action = QAction("&Refresh", self.main_window)
        refresh_action.triggered.connect(self.main_window.table_refresh)
        
        # gdrive_action = QAction("&Google Drive Sign in", self.main_window)
        # gdrive_action.triggered.connect(self.main_window.google_drive.authenticate_user)
        
        # gdrive_folder_action = QAction("&Folder", self.main_window)
        # gdrive_folder_action.triggered.connect(self.main_window.google_drive.find_or_create_beatbank_folder)
        
        debug_action = QAction("&Debug", self.main_window)
        debug_action.triggered.connect(self.main_window.debug_print)
        
        save_as_default_action = QAction("&Save as default", self.main_window)
        save_as_default_action.triggered.connect(self.main_window.save_as_default)
        
        load_default_action = QAction("&Load default template", self.main_window)
        load_default_action.triggered.connect(self.main_window.load_default)
        
        file_menu.addAction(add_track_action)
        file_menu.addAction(refresh_action)
        file_menu.addAction(exit_action)
        # file_menu.addAction(gdrive_action)
        # file_menu.addAction(gdrive_folder_action)
        file_menu.addAction(debug_action)
        file_menu.addAction(save_as_default_action)
        file_menu.addAction(load_default_action)
    def init_edit_menu(self):
        edit_menu = self.menu_bar.addMenu("&Edit")
        
        edit_track_action = QAction("&Edit Track", self.main_window)
        edit_track_action.triggered.connect(self.main_window.edit_beat)
        
        delete_track_action = QAction("&Delete Track", self.main_window)
        delete_track_action.triggered.connect(self.main_window.delete_beat)

        edit_menu.addAction(edit_track_action)
        edit_menu.addAction(delete_track_action)

    def init_view_menu(self):
        view_menu = self.menu_bar.addMenu("&View") #
        self.view_menu = view_menu
        columns_menu = view_menu.addMenu("&Columns")
        self.init_columns_menu(columns_menu)  # Assuming this method exists
        
        show_similar_tracks_action = QAction("Always Show Similar Tracks Table", self.main_window, checkable=True)
        show_similar_tracks_action.toggled.connect(self.main_window.toggle_similar_tracks)
        view_menu.addAction(show_similar_tracks_action)

    def init_settings_menu(self):
        settings_menu = self.menu_bar.addMenu("&Settings")
        
        toggle_gdrive_action = QAction("&Toggle Google Drive", self.main_window, checkable=True)
        toggle_gdrive_action.triggered.connect(lambda checked: self.toggle_setting('gdrive_enabled', checked))
        reorder_state = self.load_reorder_state()
        edit_state = self.load_click_edit_state()
 
        toggle_reorder_action = QAction("&Allow reorder", self.main_window, checkable=True)
        toggle_reorder_action.setChecked(reorder_state)
        toggle_reorder_action.triggered.connect(lambda checked: self.main_window.toggle_reorder(checked))

        toggle_click_edit_action = QAction("&Allow click to edit", self.main_window, checkable=True)
        toggle_click_edit_action.setChecked(edit_state)
        toggle_click_edit_action.triggered.connect(lambda checked: self.main_window.toggle_click_edit(checked))

        # choose_folder_action = QAction("&Choose Folder", self.main_window)
        # choose_folder_action.triggered.connect(self.main_window.google_drive.show_folder_selection)
        
        settings_menu.addAction(toggle_gdrive_action)
        settings_menu.addAction(toggle_reorder_action)
        settings_menu.addAction(toggle_click_edit_action)
        # settings_menu.addAction(choose_folder_action) TODO:gdrive

    def load_click_edit_state(self):
        settings = QSettings("Parker Tonra", "Beat Bank")
        return settings.value("editState", False, type=bool)
    
    def toggle_setting(self, setting_name, value):
        settings = QSettings("Parker Tonra", "Beat Bank")
        settings.setValue(setting_name, value)
        # If more actions need to be done after saving (e.g., updating UI elements)
        self.apply_settings()
    
    def apply_settings(self):
        settings = QSettings("Parker Tonra", "Beat Bank")
        reorder_allowed = settings.value("reorderState", True, type=bool)
        self.table.horizontalHeader().setSectionsMovable(reorder_allowed)
        gdrive_enabled = settings.value("gdrive_enabled", False, type=bool)
        self.main_window.google_drive.setEnabled(gdrive_enabled)  # Assuming there's a way to enable/disable Google Drive

    
    def load_reorder_state(self):
        settings = QSettings("Parker Tonra", "Beat Bank")
        return settings.value("reorderState", True, type=bool)
    
    def load_settings(self):
        settings = Utils.load_settings()
        return settings
    
    def toggle_gdrive(self):
        self.main_window.google_drive.toggle_gdrive()
        
    
    def init_tools_menu(self):
        tools_menu = self.menu_bar.addMenu("&Tools")
        
        check_integrity_action = QAction("Check Song File Integrity", self.main_window)
        check_integrity_action.triggered.connect(self.main_window.check_song_file_integrity)
        
        tools_menu.addAction(check_integrity_action)

    def init_help_menu(self):
        help_menu = self.menu_bar.addMenu("&Help")
        
        read_me_action = QAction("Read Me", self.main_window)
        # Assume connection to appropriate method
        help_menu.addAction(read_me_action)

    def get_column_count(self):
        print(self.table.get_column_count())
        return self.table.get_column_count()

    #TODO submenu for columns
    def init_columns_menu(self, columns_menu):
        """
        Create menu actions to toggle column visibility.
        """

        settings = QSettings("Parker Tonra", "Beat Bank")
        table = self.table
        column_count =self.model.columnCount()
        if table is None:
            sys.exit("Error: Table model is not set.")
        for i in range(column_count):
            # get the column name
            column_name = self.model.headerData(i, Qt.Orientation.Horizontal)
            column_name = str(column_name)
            # Create a QAction for the column
            action = QAction(text=column_name, parent=self.menu_bar)
            action.setCheckable(True)
            # Retrieve the saved visibility state
            visible = settings.value(f"columnVisibility_{i}", True, type=bool)
            # Set the checkbox state
            action.setChecked(visible)
            # Define a toggle function for the column visibility

            # Toggle function for the column visibility
            action.toggled.connect(lambda checked, index=i: self.toggle_column(checked, index))
            columns_menu.addAction(action)
            
            table.setColumnHidden(i, not visible)
            
    def toggle_column(self, checked, index):
        """
        Toggle the visibility of a column in the table.
        """
        self.table.setColumnHidden(index, not checked)
        settings = QSettings("Parker Tonra", "Beat Bank")
        settings.setValue(f"columnVisibility_{index}", checked)
        settings.sync()
        print(f"Column {index} visibility set to {checked}.")