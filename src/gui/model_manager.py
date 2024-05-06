# src/gui/model_manager.py
import os, datetime
from PyQt6.QtSql import QSqlTableModel, QSqlQuery
from PyQt6.QtCore import QSortFilterProxyModel
from PyQt6.QtCore import Qt
from src.utilities.utils import Utils
import mutagen
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
        self.model.select()
        self.setup_headers()

    def set_file_path_role(self, proxy_index, file_path):
        """
        Set the file_path role for a given proxy index.
        """
        source_index = self.proxyModel.mapToSource(proxy_index)
        row = source_index.row()
        column = self.model.columnCount() - 1  # Assuming file_path is the last column
        source_index = self.model.index(row, column)
        self.model.setData(source_index, file_path, Qt.DisplayRole + 1)  # Setting custom user role for file_path

    def get_data_for_row(self, proxy_row):
        """
        Get all data for a given row in the model.
        """
        source_index = self.proxyModel.mapToSource(self.proxyModel.index(proxy_row, 0))
        row_data = {}
        for column in range(self.model.columnCount()):
            column_name = self.model.headerData(column, Qt.Orientation.Horizontal)
            row_data[column_name] = self.model.record(source_index.row()).value(column)
        return row_data
    
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
        audio = self.get_audio_data(track_path)
        query = QSqlQuery(self.database)
        query.prepare(
            "INSERT INTO tracks (title, artist, length, bpm, date_added, date_created, key, notes, path_to_ableton_project, file_path) "
            "VALUES (:title, :artist, :length, :bpm, :date_added, :date_created, :key, :notes, :path_to_ableton_project, :file_path)")
        query.bindValue(":title", audio['title'])
        query.bindValue(":artist", audio['artist'])
        query.bindValue(":length", audio['length'])
        query.bindValue(":bpm", audio['bpm'])
        query.bindValue(":date_added", audio['date_added'].strftime("%Y-%m-%d %H:%M:%S"))
        query.bindValue(":date_created", audio['date_created'].strftime("%Y-%m-%d %H:%M:%S"))
        query.bindValue(":key", audio['key'])
        query.bindValue(":notes", audio['notes'])
        query.bindValue(":path_to_ableton_project", audio['path_to_ableton_project'])
        query.bindValue(":file_path", audio['file_path'])
        if query.exec():
            self.refresh_model()
            print("Track added successfully")
        else:
            print("Failed to add track:", query.lastError().text())

    def get_audio_data(self, path):
        audio = mutagen.File(path, easy=True)
        audioObj = {
                    'title': audio.get('title', [os.path.basename(path)])[0],
                    'artist': audio.get('artist', ['Unknown'])[0],
                    'length': str(int(audio.info.length // 60)) + ':' + str(int(audio.info.length % 60)),
                    'bpm': '',
                    'date_added': datetime.datetime.now(),
                    'date_created': datetime.datetime.fromtimestamp(os.path.getctime(path)),
                    'key': 'Unknown',
                    'notes': None,
                    'path_to_ableton_project': None,
                    'file_path': path
                    }
        return audioObj
    def delete_beat_from_database(self, beat_id):
        """
        Delete a beat from the database.
        """
        answer = Utils.ask_user_bool("Delete Beat", "Are you sure you want to delete this beat?")
        if answer:
            query = QSqlQuery(self.database)
            query.prepare("DELETE FROM tracks WHERE id = :id")
            query.bindValue(":id", beat_id)
            if query.exec():
                self.refresh_model()
                print("Beat deleted successfully")
            else:
                print("Failed to delete beat:", query.lastError().text())
        else:print("Beat deletion cancelled.")
    
    def get_id_for_row(self, proxy_row):
        """
        Get the ID for a given row in the model.
        """
        source_index = self.proxyModel.mapToSource(self.proxyModel.index(proxy_row, 0))
        return self.model.record(source_index.row()).value('id')
    
    def get_file_path_for_row(self, proxy_row):
        """
        Get the file path for a given row in the model.
        """
        source_index = self.proxyModel.mapToSource(self.proxyModel.index(proxy_row, 0))
        return self.model.record(source_index.row()).value('file_path')