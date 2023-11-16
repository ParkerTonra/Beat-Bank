import sys
from PyQt6 import QtWidgets, QtGui
from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QTableWidget
from PyQt6.QtCore import QMimeData, QUrl
from PyQt6.QtGui import QDrag

class DraggableTable(QTableWidget):
    def __init__(self, *args, **kwargs):
        super(DraggableTable, self).__init__(*args, **kwargs)
        self.setDragEnabled(True)

    def startDrag(self, supportedActions):
        index = self.currentIndex()
        if not index.isValid():
            return

        # Assuming the file path is in the 5th column (change as per your table structure)
        file_path = self.item(index.row(), 4).text()

        mime_data = QMimeData()
        mime_data.setUrls([QUrl.fromLocalFile(file_path)])

        drag = QDrag(self)
        drag.setMimeData(mime_data)
        drag.exec(supportedActions)