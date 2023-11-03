from sqlalchemy import Column, Integer, String, Float, Date, Binary
from sqlalchemy.orm import relationship
from . import Base  # Import the Base object from __init__.py

class Track(Base):
    __tablename__ = 'tracks'
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String)
    BPM = Column(Float)
    length = Column(String)
    key = Column(String)
    date_created = Column(Date)
    date_added = Column(Date)
    notes = Column(String)
    path_to_file = Column(String)
    path_to_ableton_project = Column(String)
    original_artist = Column(String)
    # TODO: waveform
    # waveform = Column(Binary)  # You may want to change this based on how you handle waveforms

    # Relationship to the Versions table
    versions = relationship('Version', back_populates='track')
