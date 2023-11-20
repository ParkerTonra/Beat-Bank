import datetime
import mutagen
from database import SessionLocal
from models.track import Track
from models.version import Version
from business.track_business_model import TrackBusinessModel
import os
from models.track import Track


class TrackController:
    def __init__(self, view):
        super().__init__()
        self.model = TrackBusinessModel()
        self.view = view
        
    def add_track(self, path, new_track=True):
        if new_track == False:
            print('Adding version to database and updating "current_version"')
            self.add_new_version(path)
        else:
            self.add_new_track(path)
        return
    
    def add_new_version(self, path):
        pass #TODO: add new version to existing track
    
    def add_new_track(self, path):
        audio = mutagen.File(path, easy=True)
        title = audio.get('title', [os.path.basename(path)])[0]
        artist = audio.get('artist', ['Unknown'])[0]
        length = str(int(audio.info.length // 60)) + ':' + str(int(audio.info.length % 60))
        bpm=0  #TODO: https://gist.github.com/pschwede/3193087,
        key = 'Unknown'
        date_added=datetime.datetime.now()
        date_created=datetime.datetime.fromtimestamp(os.path.getctime(path))
        notes = None
        path_to_ableton_project = None
        
        common_properties = {
                'artist': artist,
                'length': length,
                'bpm': bpm,
                'date_added': date_added,
                'date_created': date_created,
                'key': key,
                'notes': notes,
                'path_to_ableton_project': path_to_ableton_project
                # Add other shared properties here
            }
        
        new_track = Track(
                title=audio.get('title', [os.path.basename(path)])[0],
                file_path=path,
                **common_properties
            )
        
        new_version = Version(
                title=audio.get('title', [os.path.basename(path)])[0],
                file_path=path,
                **common_properties
            )
        
        self.model.add_track(new_track, new_version)

        
    
    def already_in_database(self, path):
        return self.model.already_in_database(path)
       
    def get_tracks(self):
        tracks = self.model.get_tracks()
        return tracks
    
    def get_track(self, track_id):
        track = self.model.get_track(track_id)
        return track

    def delete_track(self, track_id):
        # Delete track logic
        self.model.delete_track(track_id)

    def update_database(self, row, column, new_value):
        pass
    
    def get_versions(self, track_id):
        track = self.model.get_track(track_id)
        return track.versions

    def update_track(self, updated_track):
        self.model.update_track(updated_track)

    # Other methods for different actions (edit, refresh, etc.)
