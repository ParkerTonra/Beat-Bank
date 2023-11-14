import sys
import os
from PyQt6.QtWidgets import QApplication
from database import init_db
from gui.main_window import MainWindow
import qdarktheme

def main():
    # Initialize the database
    init_db()

    # Create the application object
    app = QApplication(sys.argv)
    
    # Dark mode theme
    qdarktheme.setup_theme()
    
    # Create the main window
    main_window = MainWindow()

    # Show the main window
    main_window.show()

    # Enter the application's main event loop
    sys.exit(app.exec())

if __name__ == '__main__':
    main()
