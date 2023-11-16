import datetime
from models import Track, Version
from database import SessionLocal
import mutagen
import os


class TrackBusinessModel:
    def add_track(self, track_obj, version_obj):
        try:
            with SessionLocal() as session:
                session.add(track_obj)
                session.add(version_obj)
                session.commit()
        finally:
            session.close()
            
    def get_tracks(self):
        with SessionLocal() as session:
            tracks = session.query(Track).all()
        return tracks
    
    def get_track_path(self, track_id):
        with SessionLocal() as session:
            track = session.query(Track).filter(Track.id == track_id).first()
            return track.file_path
    
    def already_in_database(self, path):
        with SessionLocal() as session:
            track = session.query(Track).filter(Track.file_path == path).first()
            if track is None:
                return False
            else:
                return True