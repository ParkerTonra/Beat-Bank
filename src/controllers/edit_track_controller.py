import datetime
import mutagen
from database import SessionLocal
from models.track import Track
from models.version import Version
from business.track_business_model import TrackBusinessModel
import os
from models.track import Track


class EditTrackController:
    def __init__(self, view):
        self.model = TrackBusinessModel()
        self.view = view
        self.view.track_updated.connect(self.update_track)
        
    def update_track(self, track):
        self.model.update_track(track)