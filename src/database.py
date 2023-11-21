from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from models import Base
from contextlib import contextmanager

# Create an engine
engine = create_engine('sqlite:///music_db.sqlite3')

# Create a custom Session class
SessionLocal = sessionmaker(bind=engine)

@contextmanager
def session_scope():
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()

def init_db():
    # Create tables in the database
    Base.metadata.create_all(bind=engine)