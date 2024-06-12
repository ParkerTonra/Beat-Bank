#event_handlers.py
from PyQt6.QtCore import Qt, QTime, QMimeData, QUrl, QItemSelectionModel
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QDrag
import logging



def handleDoubleClick(self, event):
    print("Double click event 222") #edit here for double click event


def tableMouseMoveEvent(self, event):
        if not (event.buttons() & Qt.MouseButton.LeftButton):
            logging.debug("Mouse move event")
            return
        if ((event.pos() - self.dragStartPosition).manhattanLength() < QApplication.startDragDistance()):
            print("Mouse move event")
            logging.debug("Mouse move event")
            return

        item = self.table.itemAt(self.dragStartPosition)
        if item and self.isDraggableCell(item):
            print("Draggable cell")
            self.startDragOperation(item)

def startDragOperation(self, item):
    logging.debug("Starting drag operation")    
    mime_data = QMimeData()
    mime_data.setUrls([QUrl.fromLocalFile(item.text())])

    drag = QDrag(self.table)
    drag.setMimeData(mime_data)
    drag.exec(Qt.DropAction.CopyAction | Qt.DropAction.MoveAction)

def dragEnterEvent(self, event):
    if event.mimeData().hasUrls():
        event.acceptProposedAction()

def dragMoveEvent(self, event):
    if event.mimeData().hasUrls():
        event.acceptProposedAction()

def dropEvent(self, event):
    # if file or link is dropped and it's an audio file
    if event.mimeData().hasUrls() and event.mimeData().urls()[0].toLocalFile().endswith(('.mp3', '.wav', '.flac')):
        print("Adding track " + event.mimeData().urls()[0].toLocalFile() + "...")
        path = event.mimeData().urls()[0].toLocalFile()
        self.trackDropped.emit(path)
    else:
        print("Error. Unable to add track to database. Is the file an audio file?")
        event.ignore()   

