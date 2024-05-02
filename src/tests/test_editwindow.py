import sys, os
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QGridLayout, QPushButton,QListView
from PyQt6.QtCore import Qt, QModelIndex, QSettings, QAbstractListModel
from PyQt6.QtGui import QDropEvent
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from utilities.utils import Utils



class SideBar(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.sidebar_layout = QVBoxLayout()  # Define the main layout for the sidebar
        self.init_header()
        self.init_sets_view()
        self.init_buttons()

    def init_sets_view(self):
        #initialize model
        settings = QSettings("Parker Tonra", "Beat Bank")
        state = settings.value("setsModel")
        
        if state:
            print("Found old sets! Loading them now...")
            self.sets_model = SetsModel(state)
        else:
            self.sets_model = SetsModel(["test", "ting", "one two", "333"])

        #initialize view
        self.sets_view = SetsView()
        self.sets_view.setModel(self.sets_model)

        self.sets_view.setStyleSheet("QListView {background-color: #222; color: #EEE; border: none; font: 16px;}")
        
        self.sidebar_layout.addWidget(self.sets_view)
      
    def init_header(self):
        self.header = QLabel(
            text='My Sets',
            styleSheet="QLabel { color : #add8e6; font: bold 22px; }"
        )
        self.sidebar_layout.addWidget(self.header)

    def init_buttons(self):
        # Container for buttons arranged in a grid
        self.sidebarButtons_layout = QGridLayout()
        self.buttons = [
            QPushButton("New"), QPushButton("Delete"),
            QPushButton("Similar"), QPushButton("Settings")
        ]

        # Setting up button styles and connections
        for i, button in enumerate(self.buttons):
            button.setStyleSheet("background-color: #444444; color: white;")
            self.sidebarButtons_layout.addWidget(button, i // 2, i % 2)  # Arrange buttons in 2x2 grid

        # Connect buttons to functions (assuming these methods are defined in main_window)
        self.buttons[0].clicked.connect(self.new_playlist)
        self.buttons[1].clicked.connect(self.delete_playlist)
        self.buttons[2].clicked.connect(self.similar_tracks)
        self.buttons[3].clicked.connect(self.open_settings)

        # Add the grid layout of buttons to the main layout
        self.sidebar_layout.addLayout(self.sidebarButtons_layout)

    def new_playlist(self):
        # Open a dialog to create a new playlist
        newPlaylistName = Utils.ask_user("Create a new playlist", "Enter the name of the new playlist:")
        self.sets_model.addPlaylist(newPlaylistName)
    def similar_tracks(self):
        # Open a dialog to create a new playlist
        print("Similar Tracks(TODO)")
    
    def open_settings(self):
        # Open a dialog to create a new playlist
        print("Settings(TODO)")
        self.main_window
    def delete_playlist(self):
        # Remove the selected playlist
        selected = self.sets_view.selectedIndexes()
        if selected:
            answer = Utils.ask_user_bool("Delete playlist", f"Are you sure you want to delete the playlist '{selected[0].data()}'?")
            if answer:
                self.sets_model.removePlaylist(selected[0].row())
            else:
                print("Track not deleted.")


class SetsModel(QAbstractListModel):
    def __init__(self, playlists=None):
        super().__init__()
        self.playlists = playlists or []
    def data(self, index, role):
        if role == Qt.ItemDataRole.DisplayRole:
            return self.playlists[index.row()]

    def rowCount(self, index=None):
        return len(self.playlists)

    def flags(self, index: QModelIndex) -> Qt.ItemFlag:
        if not index.isValid():
            print("Invalid index")
            return Qt.ItemFlag.NoItemFlags
        return Qt.ItemFlag(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsDragEnabled | Qt.ItemFlag.ItemIsDropEnabled | Qt.ItemFlag.ItemIsEditable)
    
    def addPlaylist(self, playlist):
        self.beginInsertRows(QModelIndex(), self.rowCount(), self.rowCount())
        self.playlists.append(playlist)
        self.endInsertRows()
        settings = QSettings("Parker Tonra", "Beat Bank")
        settings.setValue("setsModel", self.playlists)

    def removePlaylist(self, position):
        self.beginRemoveRows(QModelIndex(), position, position)
        self.playlists.pop(position)
        self.endRemoveRows()
        settings = QSettings("Parker Tonra", "Beat Bank")
        settings.setValue("setsModel", self.playlists)
    
class SetsView(QListView):
    def __init__(self):
        super().__init__()
        self.setMovement(QListView.Movement.Free)
        self.setAcceptDrops(True)
        self.setDragEnabled(True)
        self.setDragDropMode(QListView.DragDropMode.InternalMove)
        self.setEditTriggers(QListView.EditTrigger.DoubleClicked)

    def startDrag(self, supportedActions: Qt.DropAction) -> None:
        print("Dragging")
        return super().startDrag(supportedActions)

    def dropEvent(self, e: QDropEvent | None) -> None:
        print
        return super().dropEvent(e)
    

app = QApplication(sys.argv)
main_window = QWidget()
edit_window = SideBar(main_window=main_window)
edit_window.setLayout(edit_window.sidebar_layout)
edit_window.show()
sys.exit(app.exec())