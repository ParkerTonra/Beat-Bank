# BeatTable.py (root)/src/gui/BeatTable.py

from PyQt6.QtCore import Qt, QTime, pyqtSignal, QSettings
from PyQt6.QtWidgets import QTableView
from PyQt6 import QtWidgets
from src.gui import event_handlers
import logging


class BeatTable(QTableView):
    trackDropped = pyqtSignal(str)
    click_edit_toggled = pyqtSignal(bool)
        
    def __init__(self, main_window, model, beat_jockey, model_manager,proxy):
        super().__init__()
        self.main_window = main_window
        self.beat_jockey = beat_jockey
        self.model_manager = model_manager
        self.proxy = proxy
        
        self.setModel(proxy)
        self.model = model
        
        #self.audio_signal.playAudioSignal.connect(self.audio_player.playAudio)
        self.lastClickTime = QTime()
        self.doubleClickInterval = QtWidgets.QApplication.doubleClickInterval()
        self.setAcceptDrops(True)
        self.setDragEnabled(True)
        self.setMinimumHeight(500)
        self.setMaximumWidth(1250)
        
        self.horizontalHeader().setSectionsMovable(True)
        self.doubleClicked.connect(self.handleDoubleClick)
        self.clicked.connect(self.handleSingleClick)
        self.selection_model = self.selectionModel()
        self.selection_model.selectionChanged.connect(self.on_selection_changed)
        self.setDragDropMode(QtWidgets.QAbstractItemView.DragDropMode.InternalMove)
        self.setDragDropOverwriteMode(False)
        self.setDropIndicatorShown(True)
        self.setDragEnabled(True)
        self.setDefaultDropAction(Qt.DropAction.MoveAction)
        # self.setSelectionBehavior(QTableView.SelectionBehavior.SelectRows) maybe
        

    def on_selection_changed(self, selected, deselected):
        """
        Slot function called when the selection in the table changes. Updates
        the selected row and beat information.
        """
        print("new row selected.")
        self.update_selected_beat()
        

    def update_selected_beat(self):
        """
        Update the selected beat information based on the current selection.
        """
        current = self.selection_model.currentIndex()
        
        print(f"Current index data: {current.data()}")
        
        if not current.isValid():
            self.selected_beat = None
            print("No beat selected.")
            return

        if self.proxy:
            row = current.row()
            row_data = self.model_manager.get_data_for_row(row)
            self.selected_beat = row_data
            print(f"Selected beat updated: {self.selected_beat}")
        else:
            print("Proxy model not defined.")
            print("Model manager not defined or missing proxy model.")
        
    
    def tableMouseMoveEvent(self, event):
        print("table mouse move event")
        event_handlers.tableMouseMoveEvent(self, event)
    def handleDoubleClick(self, event):
        print("Double-click registered")
        settings = QSettings("Parker Tonra", "Beat Bank")
        clickToEdit = settings.value("editState", type=bool)
        if clickToEdit:
            print("Double click event, editing track.")
            event_handlers.handleDoubleClick(self, event)
        else:
            print("Double click event, playing track.")
            selected_id = self.selected_beat.get('Beat ID', 'N/A')
            self.play_audio()
            
    def handleSingleClick(self, event):
        print("single click registered")
    def startDragOperation(self, item):
        event_handlers.startDragOperation(self, item)
    def dragEnterEvent(self, event):
        event_handlers.dragEnterEvent(self, event)
    def dragMoveEvent(self, event):
        event_handlers.dragMoveEvent(self, event)
    def dropEvent(self, event):
        event_handlers.dropEvent(self, event)
    
    def get_column_count(self):
        return self.model().columnCount()
    
    def play_audio(self):
        try:
            print(f"Telling Beat Jockey to play a song..")
            self.main_window.audio_player.stopMusic()
            self.beat_jockey.play_song_by_path(path=self.selected_beat.get('File Location', ''), length=self.selected_beat.get('Length', 0))
        except AttributeError as e:
            print(f"AttributeError - Failed to play audio: {e}")
            print(f"Current BeatJockey object: {self.beat_jockey}, methods: {dir(self.beat_jockey)}")
        except Exception as e:
            print(f"General Exception - Failed to play audio: {e}")
    
    def findColumnIndexByName(self, column_name):
        for column in range(self.model().columnCount()):
            if self.model().headerData(column, Qt.Orientation.Horizontal, ) == column_name:
                print(f"Found column {column_name} at index {column}")
                return column
        return -1  # Return -1 if not found


