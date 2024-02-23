#database.py (root)/src/database.py

from PyQt6.QtSql import QSqlDatabase
import sys, os

def init_db():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    print(f'Current directory: {current_dir}')
    db_path = os.path.join(current_dir, '..', 'music_db.sqlite3')
    print(f'Database path: {db_path}')
    db = QSqlDatabase.addDatabase('QSQLITE')
    db.setDatabaseName(db_path)
    
    if not db.open():
        last_error = db.lastError().text()
        print(f'Unable to open database: {last_error}')
        sys.exit(1)
    
    return db