# side_bar.py (root)/src/gui/side_bar.py pyqt6 gui class for a sidebar
from PyQt6.QtWidgets import QWidget, QSplitter, QLabel, QListWidget, QVBoxLayout, QWidget, QVBoxLayout, QPushButton, QGridLayout
from PyQt6.QtCore import Qt, QSettings
from PyQt6.QtWidgets import QMessageBox
from PyQt6.QtSql import QSqlQuery
from src.utilities.utils import Utils


class SideBar(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.sidebar_layout = QVBoxLayout()  # Set the layout for the sidebar
        self.init_header()
        self.init_sidebar_splitter()
        self.init_buttons()

    def init_system_sets(self):
        self.system_sets = QListWidget()
        system_sets = ["My Beats", "Recently Added", "Recently Played"]
        self.system_sets.addItems(system_sets)
        self.system_sets.itemClicked.connect(self.show_all_tracks)

    def init_user_sets(self):
        self.user_sets = QListWidget()
        query = QSqlQuery()
        query.prepare("SELECT name FROM user_sets")
        query.exec()
        while query.next():
            self.user_sets.addItem(query.value(0))

        self.user_sets.dragEnabled()
        self.user_sets.setAcceptDrops(True)
        self.user_sets.setDropIndicatorShown(True)
        self.user_sets.setDefaultDropAction(Qt.DropAction.MoveAction)
        self.user_sets.setDragDropMode(QListWidget.DragDropMode.InternalMove)
        
        self.user_sets.itemClicked.connect(
            lambda item: self.on_set_selected(item))

    def init_sidebar_splitter(self):
        self.sidebar_splitter = QSplitter(Qt.Orientation.Vertical)
        self.init_system_sets()
        self.init_user_sets()
        self.sidebar_splitter.addWidget(self.system_sets)
        self.sidebar_splitter.addWidget(self.user_sets)
        self.sidebar_layout.addWidget(self.sidebar_splitter)

        self.sidebar_splitter.setStretchFactor(0, 3)
        self.sidebar_splitter.setStretchFactor(1, 10)

    def init_header(self):
        self.header = QLabel('My Sets')
        self.header.setStyleSheet(
            "QLabel { color : #add8e6; font: bold 22px; }")
        self.sidebar_layout.addWidget(self.header)

    def init_buttons(self):
        self.sidebarButtons_layout = QGridLayout()
        self.buttons = [
            QPushButton("New"), QPushButton("Delete"),
            QPushButton("Similar"), QPushButton("Settings")
        ]
        for i, button in enumerate(self.buttons):
            button.setStyleSheet("background-color: #444444; color: white;")
            self.sidebarButtons_layout.addWidget(
                button, i // 2, i % 2)  # Arrange buttons in 2x2 grid

        self.buttons[0].clicked.connect(self.new_playlist)
        self.buttons[1].clicked.connect(self.delete_playlist)
        self.buttons[2].clicked.connect(self.similar_tracks)
        self.buttons[3].clicked.connect(self.open_settings)
        self.sidebar_layout.addLayout(self.sidebarButtons_layout)

    def on_set_selected(self, selected):
        self.main_window.load_set(selected.text())

    def show_all_tracks(self):
        self.main_window.load_all_tracks()

    def new_playlist(self):
        newPlaylistName = Utils.ask_user(
            "Create a new playlist", "Enter the name of the new playlist:")

        if newPlaylistName:
            query = QSqlQuery()
            query.prepare("SELECT COUNT(*) FROM user_sets WHERE name = :name")
            query.bindValue(":name", newPlaylistName)

            if query.exec():
                if query.next() and query.value(0) == 0:
                    # No playlist with this name exists, proceed to insert
                    query.prepare("INSERT INTO user_sets (name) VALUES (:name)")
                    query.bindValue(":name", newPlaylistName)

                    if query.exec():
                        self.user_sets.addItem(newPlaylistName)
                    else:
                        QMessageBox.warning("Error", "Error inserting new playlist. Playlist not added.")
                        print(
                            f"Error inserting new playlist: {query.lastError().text()}")
                else:
                    QMessageBox.warning(
                        self, "Error", f"A playlist with the name '{newPlaylistName}' already exists. Playlist not added.")
                    print(f"A playlist with the name '{newPlaylistName}' already exists.")
            else:
                QMessageBox.warning("Error", "Error checking for existing playlist. Playlist not added.")
                print(f"Error checking for existing playlist: {query.lastError().text()}")

    def delete_playlist(self):
        selected = self.user_sets.currentRow()
        if selected != -1 and Utils.ask_user_bool("Delete Track", "Are you sure you want to delete this set?"):
            self.user_sets.takeItem(selected)
            query = QSqlQuery()
            query.prepare("DELETE FROM user_sets WHERE name = :name")
            query.bindValue(":name", self.user_sets.item(selected).text())
            if not query.exec():
                QMessageBox.warning("Error", "Error deleting set. Set not deleted.")
                print(f"Error deleting set: {query.lastError().text()}")
            else:
                print("Set deleted successfully.")

    def similar_tracks(self):
        print("Similar Tracks (TODO)")

    def open_settings(self):
        print("Settings (TODO)")
