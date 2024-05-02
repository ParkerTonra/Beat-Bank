from PyQt6.QtSql import QSqlQuery, QSqlTableModel, QSqlDatabase
from PyQt6.QtCore import QObject, QDateTime, pyqtSignal
from PyQt6.QtWidgets import QFileDialog, QMessageBox

from utilities.utils import Utils
import mutagen
import os
import datetime

class DatabaseController(QObject):
    def __init__(self, db_connection):
        self.db = db_connection

    def controller_add_track(self, path=None):
        print("Adding a new track to the database...")
        if not path:
            path, _ = QFileDialog.getOpenFileName(self, "Select Audio File", "", "Audio Files (*.mp3 *.wav *.flac);;All Files (*)")
            if not path:
                print("No file selected")
                return
        audio = mutagen.File(path, easy=True)
        title = audio.get('title', [os.path.basename(path)])[0]
        artist = audio.get('artist', ['Unknown'])[0]
        length = str(int(audio.info.length // 60)) + ':' + str(int(audio.info.length % 60))
        bpm = 0  # TODO: Implement BPM calculation
        key = 'Unknown'
        date_added = datetime.datetime.now()
        date_created = datetime.datetime.fromtimestamp(os.path.getctime(path))
        notes = None
        path_to_ableton_project = None
        
        # TODO: separate SQL stuff into another function
        # Prepare SQL query for inserting the new track
        query = QSqlQuery()
        query.prepare("INSERT INTO tracks (title, artist, length, bpm, key, date_added, date_created, notes, path_to_ableton_project, file_path) "
                    "VALUES (:title, :artist, :length, :bpm, :key, :date_added, :date_created, :notes, :path_to_ableton_project, :file_path)")

        query.bindValue(":title", title)
        query.bindValue(":artist", artist)
        query.bindValue(":length", length)
        query.bindValue(":bpm", bpm)
        query.bindValue(":key", key)
        query.bindValue(":date_added", QDateTime(date_added).date())
        query.bindValue(":date_created", QDateTime(date_created).date())
        query.bindValue(":notes", notes)
        query.bindValue(":path_to_ableton_project", path_to_ableton_project)
        query.bindValue(":file_path", path)

        # Execute query
        if query.exec():
            print(f"Adding track to database: {title} by {artist}")
            return True
        else:
            print("Failed to add track:", query.lastError().text())
            return False
    
    def controller_delete_beat(self, selected_row):
        if selected_row < 0:
            Utils.warn_user("Error.", "No track selected.")
            return
        
        reply = Utils.ask_user("Delete Track", "Are you sure you want to delete this track?")
        
        if reply == QMessageBox.StandardButton.Yes:
            track_id = self.model.record(selected_row).value("id")
            self.delete_from_database(track_id)
            self.table_refresh()
        else:
            print("Track deletion cancelled.")
            return
    
    def get_tracks(self):
        # Logic to fetch tracks from the database
        pass

    def update_track(self, track_id, new_data):
        # Logic to update a track
        pass

    