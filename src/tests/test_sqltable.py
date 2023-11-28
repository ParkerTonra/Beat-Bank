# test_sqltable.py
import sys, os, qdarktheme
from PyQt6.QtWidgets import QApplication, QMainWindow, QTableView
from PyQt6.QtSql import QSqlTableModel, QSqlDatabase

src_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, src_dir)
from database import init_db


class SqlTestWindow(QMainWindow):
    def __init__(self, db):
        super().__init__()
        self.db = db
        self.init_ui()
 
    def init_ui(self):
        print("Initializing UI for main window...")
        self.setWindowTitle('Beat Bank Test')
        self.setGeometry(100, 100, 1400, 200)
        
        self.table_view = QTableView()
        self.setCentralWidget(self.table_view)
        
        self.model = QSqlTableModel(self, self.db)
        self.model.setTable('tracks')
        self.model.setEditStrategy(QSqlTableModel.EditStrategy.OnFieldChange)
        self.model.select()
        
        self.table_view.setModel(self.model)
        
        self.table_view.resizeColumnsToContents()

def main():
    # Initialize the database
    if not init_db():
        print('Unable to open database')
        sys.exit(1)  # Exit the application if the database can't be opened

    # Create the application object
    app = QApplication(sys.argv)
    
    # Dark mode theme
    qdarktheme.setup_theme()
    
    # Create the main window
    db = QSqlDatabase.database()
    main_window = SqlTestWindow(db)

    # Show the main window
    main_window.show()

    # Enter the application's main event loop
    sys.exit(app.exec())

if __name__ == '__main__':
    main()

