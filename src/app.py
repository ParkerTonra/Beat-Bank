# app.py (root)/src/app.py

import sys, qdarktheme
from PyQt6.QtWidgets import QApplication
from PyQt6.QtSql import QSqlDatabase
from database import init_db
from gui.BeatBank import MainWindow

def main():
    # Create the application object
    app = QApplication(sys.argv)
    
    # Dark mode theme
    qdarktheme.setup_theme()
    
    # Initialize the database
    init_db()

    # Create the main window
    main_window = MainWindow()

    # Show the main window
    main_window.show()

    # Enter the application's main event loop
    sys.exit(app.exec())

if __name__ == '__main__':
    main()
