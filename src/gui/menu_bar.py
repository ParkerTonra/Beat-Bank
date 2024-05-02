from PyQt6.QtCore import QSettings, Qt
from PyQt6.QtGui import QAction
from utilities.utils import Utils

class InitializeMenuBar:
    # Init functions
    def __init__(self, main_window):
        self.main_window = main_window
        self.menu_bar = main_window.menuBar()

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
        
        gdrive_action = QAction("&Google Drive Sign in", self.main_window)
        gdrive_action.triggered.connect(self.main_window.google_drive.authenticate_user)
        
        gdrive_folder_action = QAction("&Folder", self.main_window)
        gdrive_folder_action.triggered.connect(self.main_window.google_drive.find_or_create_beatbank_folder)
        
        debug_action = QAction("&Debug", self.main_window)
        debug_action.triggered.connect(self.main_window.debug_print)
        
        save_as_default_action = QAction("&Save as default", self.main_window)
        save_as_default_action.triggered.connect(self.main_window.save_as_default)
        
        load_default_action = QAction("&Load default template", self.main_window)
        load_default_action.triggered.connect(self.main_window.load_default)
        
        file_menu.addAction(add_track_action)
        file_menu.addAction(refresh_action)
        file_menu.addAction(exit_action)
        file_menu.addAction(gdrive_action)
        file_menu.addAction(gdrive_folder_action)
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
        # Restore the reorder state for the UI component
        settings = QSettings("Parker Tonra", "Beat Bank")
        reorder_state = settings.value("reorderState", True, type=bool)  # Default to True if not set
        
        settings_menu = self.menu_bar.addMenu("&Settings")
        
        toggle_gdrive_action = QAction("&Toggle Google Drive", self.main_window, checkable=True)
        toggle_gdrive_action.triggered.connect(lambda checked: self.main_window.google_drive.toggle_gdrive(checked))
        
        toggle_reorder_action = QAction("&Allow reorder", self.main_window, checkable=True)
        toggle_reorder_action.setChecked(reorder_state)
        toggle_reorder_action.triggered.connect(lambda checked: self.main_window.toggle_reorder(checked))

        
        toggle_click_edit = QAction("&Allow click to edit", self.main_window, checkable=True)
        toggle_click_edit.triggered.connect(lambda checked: self.main_window.toggle_click_edit(checked))

        choose_folder_action = QAction("&Choose Folder", self.main_window)
        choose_folder_action.triggered.connect(self.main_window.google_drive.show_folder_selection)
        
        settings_menu.addAction(toggle_gdrive_action)
        settings_menu.addAction(toggle_reorder_action)
        settings_menu.addAction(toggle_click_edit)
        settings_menu.addAction(choose_folder_action)

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
        
    #TODO submenu for columns
    def init_columns_menu(self, columns_menu):
        table = self.main_window.table
        for i in range(table.model().columnCount()):
            column_name = table.model().headerData(i, Qt.Orientation.Horizontal)
            action = QAction(column_name, self.main_window, checkable=True)
            settings = QSettings("Parker Tonra", "Beat Bank") #TODO
            action.setChecked(not table.isColumnHidden(i))
            # Here you should use a different approach because using lambda in a loop can cause unexpected behavior
            def toggle_column(checked, index=i):
                self.main_window.toggle_column(checked, index)

            action.toggled.connect(toggle_column)
            columns_menu.addAction(action)
