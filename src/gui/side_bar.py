# side_bar.py (root)/src/gui/side_bar.py pyqt6 gui class for a sidebar
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget, QGridLayout, QSizePolicy
from PyQt6.QtCore import Qt

class SideBar(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.layout = QVBoxLayout()  # Define the main layout for the sidebar
        self.init_table()
        self.init_buttons()

    

    def init_table(self):
        # Create a table widget for displaying items like playlists or tracks
        self.sidebar_table = QTableWidget()
        self.sidebar_table.setRowCount(10)  # Placeholder for row count
        self.sidebar_table.setColumnCount(1)  # Single column for item names
        self.sidebar_table.setHorizontalHeaderLabels(['Playlists'])  # Set the header label
        self.sidebar_table.verticalHeader().setVisible(False)  # Hide the vertical header
        self.sidebar_table.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding)  # Set size policy
        self.layout.addWidget(self.sidebar_table)  # Add the table to the sidebar layout

    def init_buttons(self):
        # Container for buttons arranged in a grid
        self.sidebarButtons_layout = QGridLayout()
        self.buttons = [
            QPushButton("1"), QPushButton("2"),
            QPushButton("3"), QPushButton("4")
        ]

        # Setting up button styles and connections
        for i, button in enumerate(self.buttons):
            button.setStyleSheet("background-color: #444444; color: white;")
            self.sidebarButtons_layout.addWidget(button, i // 2, i % 2)  # Arrange buttons in 2x2 grid

        # Connect buttons to functions (assuming these methods are defined in main_window)
        self.buttons[0].clicked.connect(self.main_window.add_playlist)
        self.buttons[1].clicked.connect(self.main_window.remove_playlist)
        self.buttons[2].clicked.connect(self.main_window.show_similar_tracks)
        self.buttons[3].clicked.connect(self.main_window.open_settings)

        # Add the grid layout of buttons to the main layout
        self.layout.addLayout(self.sidebarButtons_layout)

        # Set the sidebar's layout
        self.setLayout(self.layout)

