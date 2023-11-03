import sys
import os
from PyQt5.QtWidgets import QApplication
from database import init_db
from gui.main_window import MainWindow

def main():
    # Initialize the database
    init_db()

    # Create the application object
    app = QApplication(sys.argv)

    # Create the main window
    main_window = MainWindow()

    # Show the main window
    main_window.show()

    # Enter the application's main event loop
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
