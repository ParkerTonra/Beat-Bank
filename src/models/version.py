from sqlalchemy import Column, Integer, String, Date, ForeignKey, Binary
from sqlalchemy.orm import relationship
from . import Base

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
    waveform = Column(Binary)  # You may want to change this based on how you handle waveforms

    # Relationship to the Tracks table
    track = relationship('Track', back_populates='versions')