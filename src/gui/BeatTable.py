# BeatTable.py (root)/src/gui/BeatTable.py

from PyQt6.QtCore import Qt, QTime, pyqtSignal, QSettings
from PyQt6.QtWidgets import QTableView, QHeaderView
from PyQt6 import QtWidgets
from PyQt6.QtCore import pyqtSignal
from gui import event_handlers, play_audio
from gui.signals import PlayAudioSignal

class BeatTable(QTableView):
    trackDropped = pyqtSignal(str)
    click_edit_toggled = pyqtSignal(bool)
    
    def __init__(self, parent=None, audio_signal=None):
        super().__init__(parent)
        if audio_signal is not None:
            print("signal linked!")
            self.audio_signal = audio_signal
        else:
            self.audio_signal = PlayAudioSignal()
        print("audio_signal: ", audio_signal)
        self.audio_player = play_audio.AudioPlayer()
        self.lastClickTime = QTime()
        self.doubleClickInterval = QtWidgets.QApplication.doubleClickInterval()
        self.setAcceptDrops(True)
        self.setDragEnabled(True)
        self.setMinimumHeight(500)
        self.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        self.horizontalHeader().setSectionsMovable(True)
        

    def handleSingleClick(self, event):
        event_handlers.handleSingleClick(self, event)
        print("Single click handled")
    def tableMouseMoveEvent(self, event):
        event_handlers.tableMouseMoveEvent(self, event)
    def mousePressEvent(self, event) -> None:
        event_handlers.tableMousePressEvent(self, event)
    def handleDoubleClick(self, event):
        settings = QSettings("Parker Tonra", "Beat Bank")
        clickToEdit = settings.value("clickToEdit", type=bool)
        if clickToEdit:
            event_handlers.handleDoubleClick(self, event)
        else:
            print("not in edit mode, so not handling double click event")
            event_handlers.doubleClickPlay(self, event)
        
    def startDragOperation(self, item):
        event_handlers.startDragOperation(self, item)
    def dragEnterEvent(self, event):
        event_handlers.dragEnterEvent(self, event)
    def dragMoveEvent(self, event):
        event_handlers.dragMoveEvent(self, event)
    def dropEvent(self, event):
        event_handlers.dropEvent(self, event)
    def play_audio(self):
        #emit a signal to play the audio
        self.audio_signal.playAudioSignal.emit()
        print("Playing audio...")
        
    
    def findColumnIndexByName(self, column_name):
        for column in range(self.model().columnCount()):
            if self.model().headerData(column, Qt.Orientation.Horizontal, ) == column_name:
                print(f"Found column {column_name} at index {column}")
                return column
        return -1  # Return -1 if not found


