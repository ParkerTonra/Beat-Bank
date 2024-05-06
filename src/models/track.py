from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey
from sqlalchemy.orm import relationship
from src.models import Base  # Import the Base object from __init__.py

class Track(Base):
    __tablename__ = 'tracks'
    __table_args__ = {'extend_existing': True}
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String)
    artist = Column(String)
    bpm = Column(Float)
    length = Column(String)
    key = Column(String)
    date_created = Column(Date)
    date_added = Column(Date)
    notes = Column(String)
    file_path = Column(String)
    path_to_ableton_project = Column(String)
    
    current_version_id = Column(Integer, ForeignKey('versions.id'))
    current_version = relationship('Version', foreign_keys=[current_version_id], back_populates='track', uselist=False)
    versions = relationship('Version', back_populates='track', foreign_keys='Version.track_id', cascade='all, delete-orphan')
    # TODO: waveform
    # waveform = Column(Binary)  # You may want to change this based on how you handle waveforms



