from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.models import Base

# Create an engine
engine = create_engine('sqlite:///music_db.sqlite3')

# Create a custom Session class
SessionLocal = sessionmaker(bind=engine)

def init_db():
    # Create tables in the database
    Base.metadata.create_all(bind=engine)