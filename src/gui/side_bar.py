# side_bar.py (root)/src/gui/side_bar.py pyqt6 gui class for a sidebar
from PyQt6.QtWidgets import QWidget, QLabel, QListWidget, QVBoxLayout, QWidget, QVBoxLayout, QPushButton, QGridLayout
from PyQt6.QtCore import Qt, QSettings
from utilities.utils import Utils

class SideBar(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.sidebar_layout = QVBoxLayout()  # Set the layout for the sidebar
        self.init_header()
        self.init_sets_list()
        self.init_buttons()

    def init_sets_list(self):
        # Load saved playlists or initialize default ones
        settings = QSettings("Parker Tonra", "Beat Bank")
        state = settings.value("setsList")
        if state is None:
            state = ["All Tracks", "Favorites", "Recently Played"]
            settings.setValue("setsList", state)
        self.sets_list = QListWidget()
        self.sets_list.addItems(state)
        self.sets_list.dragEnabled()
        self.sets_list.setAcceptDrops(True)
        self.sets_list.setDropIndicatorShown(True)
        self.sets_list.setDefaultDropAction(Qt.DropAction.MoveAction)
        self.sets_list.setDragDropMode(QListWidget.DragDropMode.InternalMove)
        self.sidebar_layout.addWidget(self.sets_list)

    def init_header(self):
        self.header = QLabel('My Sets')
        self.header.setStyleSheet("QLabel { color : #add8e6; font: bold 22px; }")
        self.sidebar_layout.addWidget(self.header)

    def init_buttons(self):
        self.sidebarButtons_layout = QGridLayout()
        self.buttons = [
            QPushButton("New"), QPushButton("Delete"),
            QPushButton("Similar"), QPushButton("Settings")
        ]
        for i, button in enumerate(self.buttons):
            button.setStyleSheet("background-color: #444444; color: white;")
            self.sidebarButtons_layout.addWidget(button, i // 2, i % 2)  # Arrange buttons in 2x2 grid
        
        self.buttons[0].clicked.connect(self.new_playlist)
        self.buttons[1].clicked.connect(self.delete_playlist)
        self.buttons[2].clicked.connect(self.similar_tracks)
        self.buttons[3].clicked.connect(self.open_settings)
        self.sidebar_layout.addLayout(self.sidebarButtons_layout)

    def new_playlist(self):
        newPlaylistName = Utils.ask_user("Create a new playlist", "Enter the name of the new playlist:")
        if newPlaylistName:
            self.sets_list.addItem(newPlaylistName)
            self.save_playlists()

    def delete_playlist(self):
        selected = self.sets_list.currentRow()
        if selected != -1 and Utils.ask_user_bool("Delete Track", "Are you sure you want to delete this set?"):
            self.sets_list.takeItem(selected)
            self.save_playlists()

    def similar_tracks(self):
        print("Similar Tracks (TODO)")

    def open_settings(self):
        print("Settings (TODO)")

    def save_playlists(self):
        playlists = [self.sets_list.item(i).text() for i in range(self.sets_list.count())]
        settings = QSettings("Parker Tonra", "Beat Bank")
        settings.setValue("setsList", playlists)
