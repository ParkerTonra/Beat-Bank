from sqlalchemy import create_engine
from src.models import Base

def setup_database():
    # Create an engine
    engine = create_engine('sqlite:///music_db.sqlite3') # create 

    # Create the tables
    Base.metadata.create_all(engine)

if __name__ == '__main__':
    setup_database()