# app.py (root)/src/app.py

from PyQt6.QtWidgets import QApplication
from src.gui.BeatBank import MainWindow
from src.logging_config import setup_logging
import sys
import qdarktheme
import logging
from database import init_db

setup_logging()
logger = logging.getLogger(__name__)


def main():
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
