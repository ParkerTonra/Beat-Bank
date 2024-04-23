from PyQt6.QtGui import QColor, QBrush
from PyQt6.QtWidgets import QStyledItemDelegate

class InvalidFileDelegate(QStyledItemDelegate):
    def __init__(self, parent=None):
        super().__init__(parent)
        # A set to keep track of rows that have invalid file paths
        self.invalid_rows = set()

    def paint(self, painter, option, index):
        if index.row() in self.invalid_rows:
            option.backgroundBrush = QBrush(QColor(255, 200, 200))  # Light red
        super().paint(painter, option, index)

    def set_invalid_rows(self, rows):
        self.invalid_rows = set(rows)
        self.parent().viewport().update()  # Update the view to reflect changes