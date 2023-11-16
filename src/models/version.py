from sqlalchemy import Column, Integer, String, Date, ForeignKey
from sqlalchemy.orm import relationship
from models import Base

class Version(Base):
    __tablename__ = 'versions'
    id = Column(Integer, primary_key=True, autoincrement=True)
    track_id = Column(Integer, ForeignKey('tracks.id'))
    title = Column(String)
    length = Column(String)
    key = Column(String)
    date_created = Column(Date)
    date_added = Column(Date)
    notes = Column(String)
    path_to_file = Column(String)
    path_to_ableton_project = Column(String)
    original_artist = Column(String)
    #TODO: waveform = Column(Binary)  # You may want to change this based on how you handle waveforms

    # Relationship to the Tracks table
    track = relationship('Track', foreign_keys=[track_id], back_populates='versions')