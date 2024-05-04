# app.py (root)/src/app.py

import sys, qdarktheme
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import qDebug
from database import init_db
from gui.BeatBank import MainWindow
def setup_debugging():
    class QDebugStream:
        def write(self, message):
            qDebug(message.strip()) 
        def flush(self):
            pass

    sys.stdout = QDebugStream()
    sys.stderr = QDebugStream()
    
    
    
def main():
    setup_debugging()
    # Create the application object
    app = QApplication(sys.argv)
    
    # Dark mode theme
    qdarktheme.setup_theme()
    
    # Initialize the database
    db = init_db()

    # Create the main window
    main_window = MainWindow(db)

    # Show the main window
    main_window.show()
    # Enter the application's main event loop

    sys.exit(app.exec())
    
if __name__ == '__main__':
    main()
