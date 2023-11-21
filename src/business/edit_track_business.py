import datetime
from models import Track, Version
from database import SessionLocal
import mutagen
import os

class EditTrackBusinessModel:
    def update_track(self, track):
        with SessionLocal() as session:
            try:
                session.merge(track)  # Merge the updated track object
                session.commit()
                print("Track updated successfully in the database.")
            except Exception as e:
                print(f"An error occurred: {e}")
                session.rollback()