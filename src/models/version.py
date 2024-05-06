from sqlalchemy import Column, Integer, String, Date, ForeignKey, Float
from sqlalchemy.orm import relationship
from src.models import Base

class Version(Base):
    __tablename__ = 'versions'
    __table_args__ = {'extend_existing': True}
    id = Column(Integer, primary_key=True, autoincrement=True)
    track_id = Column(Integer, ForeignKey('tracks.id'))
    title = Column(String)
    artist = Column(String)
    length = Column(String)
    key = Column(String)
    date_added = Column(Date)
    date_created = Column(Date)
    notes = Column(String)
    file_path = Column(String)
    path_to_ableton_project = Column(String)
    bpm = Column(Float)
    # Relationship to the Tracks table
    track = relationship('Track', foreign_keys=[track_id], back_populates='versions')
    #TODO: waveform = Column(Binary)  
    
