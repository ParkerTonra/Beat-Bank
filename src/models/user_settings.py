from sqlalchemy import Column, Integer, String, Date, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from models import Base


class UserSettings(Base):
    __tablename__ = 'user_settings'
    id = Column(Integer, primary_key=True, autoincrement=True)
    developer_mode = Column(Boolean, default=False)
    dark_mode = Column(Boolean, default=True)
    # local library mode (big)
    
    