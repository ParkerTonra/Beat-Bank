# src/gui/model_manager.py
from PyQt6.QtSql import QSqlTableModel, QSqlQuery
from PyQt6.QtCore import QSortFilterProxyModel
from PyQt6.QtCore import Qt

class ModelManager:
    def __init__(self, database, parent=None):
        self.database = database
        self.parent = parent
        self.model = None
        self.proxyModel = None

    def setup_models(self):
        self.init_beat_model()
        self.init_proxy_model()

    def init_beat_model(self):
        """
        Initialize the QSqlTableModel and configure it.
        """
        self.model = QSqlTableModel(self.parent, self.database)
        self.model.setTable('tracks')
        self.model.setEditStrategy(QSqlTableModel.EditStrategy.OnFieldChange)
        self.model.select()
        self.setup_headers()

    def setup_headers(self):
        """
        Set up readable column names for the model.
        """
        column_headers = {
            0: 'Beat ID',
            1: 'Title',
            2: 'Length',
            3: 'Key',
            4: 'Date Created',
            5: 'Date Added',
            6: 'Notes',
            7: 'File Location',
            8: 'Ableton File Location',
            9: 'Artist',
            10: 'Current Version ID',
            11: 'Tempo'
        }
        for column, header in column_headers.items():
            self.model.setHeaderData(column, Qt.Orientation.Horizontal, header)

    def init_proxy_model(self):
        """
        Initialize the QSortFilterProxyModel and set the source model.
        """
        self.proxyModel = QSortFilterProxyModel(self.parent)
        self.proxyModel.setSourceModel(self.model)

    def refresh_model(self):
        """
        Refresh the QSqlTableModel.
        """
        print("Refreshing table...")
        self.model.select()

    def add_track_to_database(self, track_path):
        """
        Add a new track to the database.
        """
        query = QSqlQuery(self.database)
        query.prepare("INSERT INTO tracks (file_path) VALUES (:file_path)")
        query.bindValue(":file_path", track_path)
        if query.exec():
            self.refresh_model()
            print("Track added successfully")
        else:
            print("Failed to add track:", query.lastError().text())
