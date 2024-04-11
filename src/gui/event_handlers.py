from PyQt6.QtCore import Qt, QTime, QMimeData, QUrl, QItemSelectionModel
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QDrag

def tableMousePressEvent(self, event):
    print("Table mouse press event")
    if event.button() == Qt.MouseButton.LeftButton:
        current_time = QTime.currentTime()

        if not self.lastClickTime.isNull() and \
           self.lastClickTime.msecsTo(current_time) < self.doubleClickInterval:
            print("Double click event")
            self.handleDoubleClick(event)
        else:
            print("Single click event")
            self.handleSingleClick(event)
        
        self.lastClickTime = current_time
        
def handleSingleClick(self, event):
    index = self.indexAt(event.pos())
    
    if index.isValid():
        print(f"Item clicked at row {index.row()}, column {index.column()}")
        # Select the row
        selectionModel = self.selectionModel()
        selectionModel.clearSelection()
        
        # PyQt6 way of specifying selection flags
        flags = QItemSelectionModel.SelectionFlag.Select | QItemSelectionModel.SelectionFlag.Rows
        
        # Using the select method with the correct flags
        selectionModel.select(index, flags)
        
    self.dragStartPosition = event.pos()

def handleDoubleClick(self, event):
    print("Double click event")
    index = self.indexAt(event.pos())
    if index.isValid():
        print(f"Double clicked in row {index.row()}, column {index.column()}")
        self.edit(index)

def doubleClickPlay(self, event):
    index = self.indexAt(event.pos())
    if index.isValid():
        self.play_audio()

def tableMouseMoveEvent(self, event):
        if not (event.buttons() & Qt.MouseButton.LeftButton):
            return
        if ((event.pos() - self.dragStartPosition).manhattanLength() < QApplication.startDragDistance()):
            print("Mouse move event")
            return

        item = self.table.itemAt(self.dragStartPosition)
        if item and self.isDraggableCell(item):
            print("Draggable cell")
            self.startDragOperation(item)

def startDragOperation(self, item):
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

