from PyQt6 import QtCore
from PyQt6.QtCore import pyqtSignal

class PlayAudioSignal(QtCore.QObject):
    playAudioSignal = pyqtSignal(str)