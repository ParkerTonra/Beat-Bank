# side_bar.py (root)/src/gui/side_bar.py pyqt6 gui class for a sidebar
from PyQt6.QtWidgets import QWidget, QLabel, QListView, QVBoxLayout, QWidget, QVBoxLayout, QPushButton, QGridLayout
from PyQt6.QtCore import Qt, QAbstractListModel, QModelIndex, QSettings, QMimeData, QByteArray, QDataStream, QIODevice
from PyQt6.QtGui import QDropEvent, QDrag, QDragEnterEvent
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
    
    def data(self, index, role):
        if role == Qt.ItemDataRole.DisplayRole:
            return self.playlists[index.row()]

    def setData(self, index, value, role):
        if role == Qt.ItemDataRole.EditRole:
            self.playlists[index.row()] = value
            self.dataChanged.emit(index, index, [role])
            return True
        return False
    
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

    def rowCount(self, parent=QModelIndex()):
        return len(self.playlists)

    def flags(self, index: QModelIndex) -> Qt.ItemFlag:
        if not index.isValid():
            print("Invalid index")
            return Qt.ItemFlag.NoItemFlags
        return Qt.ItemFlag(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsDragEnabled | Qt.ItemFlag.ItemIsDropEnabled | Qt.ItemFlag.ItemIsEditable)
    
    def data(self, index, role):
        if role == Qt.ItemDataRole.DisplayRole:
            return self.playlists[index.row()]

    def setData(self, index, value, role):
        if role == Qt.ItemDataRole.EditRole:
            self.playlists[index.row()] = value
            self.dataChanged.emit(index, index, [role])
            return True
        return False
    
    def addPlaylist(self, playlist):
        self.beginInsertRows(QModelIndex(), self.rowCount(), self.rowCount())
        self.playlists.append(playlist)
        self.endInsertRows()
        settings = QSettings("Parker Tonra", "Beat Bank")
        settings.setValue("setsModel", self.playlists)

    def removePlaylist(self, position):
        if position < 0 or position >= len(self.playlists):
            return False
        self.beginRemoveRows(QModelIndex(), position, position)
        self.playlists.pop(position)
        self.endRemoveRows()
        settings = QSettings("Parker Tonra", "Beat Bank")
        settings.setValue("setsModel", self.playlists)
        return True
    def mimeTypes(self):
        return ['application/vnd.qt.item.list']

    def mimeData(self, indexes):
        mime_data = QMimeData()
        encoded_data = QByteArray()
        stream = QDataStream(encoded_data, QIODevice.OpenModeFlag.WriteOnly)

        for index in indexes:
            if index.isValid():
                text = self.data(index, Qt.ItemDataRole.DisplayRole)
                if isinstance(text, str):
                    text = text.encode('utf-8')
                stream.writeString(text)

        mime_data.setData('application/vnd.qt.item.list', encoded_data)
        return mime_data

    def moveRows(self, sourceParent, sourceRow, count, destinationParent, destinationChild):
        # Validate input to prevent crashes
        if sourceRow < 0 or destinationChild < 0 or sourceRow >= self.rowCount() or destinationChild > self.rowCount():
            return False

        self.layoutAboutToBeChanged.emit()
        
        # Adjust destination for items moving downwards
        if destinationChild > sourceRow:
            destinationChild -= count
            if destinationChild <= sourceRow:
                destinationChild = sourceRow + count

        # Perform the row move
        if sourceRow < destinationChild:
            range_start = sourceRow
            range_end = sourceRow + count - 1
            insert_position = destinationChild
        else:
            range_start = sourceRow + count - 1
            range_end = sourceRow
            insert_position = destinationChild

        self.beginMoveRows(QModelIndex(), range_start, range_end, QModelIndex(), insert_position)
        if sourceRow < destinationChild:
            for _ in range(count):
                self.playlists.insert(destinationChild - 1, self.playlists.pop(sourceRow))
                destinationChild -= 1
        else:
            for _ in range(count):
                self.playlists.insert(destinationChild, self.playlists.pop(sourceRow + count - 1))

        self.endMoveRows()

        self.layoutChanged.emit()

        # Save the new state
        settings = QSettings("Parker Tonra", "Beat Bank")
        settings.setValue("setsModel", self.playlists)

        return True

        
    def dropMimeData(self, data, action, row, column, parent):
        if action == Qt.DropAction.IgnoreAction:
            return True

        if not data.hasFormat('application/vnd.qt.item.list'):
            return False

        if column > 0:
            return False  # Ensure drops are only handled for the first column

        stream = QDataStream(data.data('application/vnd.qt.item.list'), QIODevice.OpenModeFlag.ReadOnly)
        new_items = []
        while not stream.atEnd():
            text = stream.readString()
            new_items.append(text)

        if row == -1:
            if parent.isValid():
                row = parent.row()
            else:
                row = self.rowCount()

        for text in new_items:
            self.beginInsertRows(QModelIndex(), row, row)
            self.playlists.insert(row, text)
            row += 1
            self.endInsertRows()

        return True


class SetsView(QListView):
    def __init__(self):
        super().__init__()
        self.setAcceptDrops(True)
        self.setDragEnabled(True)
        self.setDragDropMode(QListView.DragDropMode.InternalMove)
        self.setDefaultDropAction(Qt.DropAction.MoveAction)
        self.setEditTriggers(QListView.EditTrigger.SelectedClicked | QListView.EditTrigger.DoubleClicked)
        # add some padding in between items
        self.setSpacing(5)
        
        

    def startDrag(self, actions):
        drag = QDrag(self)
        mime = self.model().mimeData(self.selectedIndexes())
        drag.setMimeData(mime)
        drag.exec(actions)
        
    def dragEnterEvent(self, event):
        print("Drag Enter")
        if event.mimeData().hasFormat('application/vnd.qt.item.list'):
            event.setAccepted(True)
        else:
            event.setAccepted(False)
    def dropEvent(self, e: QDropEvent | None) -> None:
        print("Dropping event")
        return super().dropEvent(e)
    
