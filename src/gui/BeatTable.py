# BeatTable.py (root)/src/gui/BeatTable.py

from PyQt6.QtCore import Qt, QTime, pyqtSignal, QSettings
from PyQt6.QtWidgets import QTableView, QHeaderView
from PyQt6 import QtWidgets
from PyQt6.QtCore import pyqtSignal
from gui import event_handlers, play_audio
from gui.signals import PlayAudioSignal
from gui.play_audio import AudioPlayer

class BeatTable(QTableView):
    trackDropped = pyqtSignal(str)
    click_edit_toggled = pyqtSignal(bool)
    
    def __init__(self, parent=None, audio_signal=None):
        super(BeatTable, self).__init__(parent)
        self.parent = parent
        self.main_window = parent
        if audio_signal is not None:
            self.audio_signal = audio_signal
        else:
            self.audio_signal = PlayAudioSignal()
        
        self.audio_player = AudioPlayer(parent)
        self.audio_signal.playAudioSignal.connect(self.audio_player.playAudio)
        self.lastClickTime = QTime()
        self.doubleClickInterval = QtWidgets.QApplication.doubleClickInterval()
        self.setAcceptDrops(True)
        self.setDragEnabled(True)
        self.setMinimumHeight(500)
        self.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        self.horizontalHeader().setSectionsMovable(True)
        self.doubleClicked.connect(self.handleDoubleClick)
        

    def update_selected_beat(self, current, previous):
        """
        Update the selected beat information based on the current selection.
        """
        if not current.isValid():
            self.selected_beat = None
            print("No beat selected.")
            return

        # Assuming `current` is a QModelIndex, map it if using a proxy model
        if hasattr(self, 'model_manager') and self.model_manager.proxyModel:
            source_index = self.model_manager.proxyModel.mapToSource(current)
            row_data = {self.model_manager.model.headerData(i, Qt.Orientation.Horizontal): self.model_manager.model.record(source_index.row()).value(i) for i in range(self.model_manager.model.columnCount())}
            self.selected_beat = row_data
            print(f"Selected track updated(BT))")
        else:
            print("Model manager not defined or missing proxy model.")
        
    
    def tableMouseMoveEvent(self, event):
        print("table mouse move event")
        event_handlers.tableMouseMoveEvent(self, event)
    def handleDoubleClick(self, event):
        settings = QSettings("Parker Tonra", "Beat Bank")
        clickToEdit = settings.value("clickToEdit", type=bool)
        if clickToEdit:
            event_handlers.handleDoubleClick(self, event)
        else:
            self.play_audio()
            
        
    def startDragOperation(self, item):
        event_handlers.startDragOperation(self, item)
    def dragEnterEvent(self, event):
        event_handlers.dragEnterEvent(self, event)
    def dragMoveEvent(self, event):
        event_handlers.dragMoveEvent(self, event)
    def dropEvent(self, event):
        event_handlers.dropEvent(self, event)
    def play_audio(self):
        path = self.parent.get_selected_beat_path()
        #emit a signal to play the audio
        if path:
            self.audio_signal.playAudioSignal.emit(path)
        print("Playing audio...")
        
    
    def findColumnIndexByName(self, column_name):
        for column in range(self.model().columnCount()):
            if self.model().headerData(column, Qt.Orientation.Horizontal, ) == column_name:
                print(f"Found column {column_name} at index {column}")
                return column
        return -1  # Return -1 if not found


