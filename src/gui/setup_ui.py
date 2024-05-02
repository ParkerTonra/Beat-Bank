from PyQt6.QtWidgets import (
    QMainWindow, QVBoxLayout, QWidget, QHBoxLayout, QTableView, QFrame, QSplitter, QHeaderView
)

from gui.BeatTable import BeatTable
from gui.side_bar import SideBar
from gui.menu_bar import InitializeMenuBar
from gui.InvalidFileDelegate import InvalidFileDelegate
from gui.model_manager import ModelManager

class MainWindowSetup(QMainWindow):
    def __init__(self, model_manager, audio_signal):
        super().__init__()
        self.model_manager = model_manager
        self.audio_signal = audio_signal
        self.init_ui()

    def init_ui(self):
        self.setupWindow()
        self.init_side_bar()
        self.init_beat_table()
        self.declare_layouts()
        self.init_setupLayouts()
        self.finalizeLayout()

    def setupWindow(self):
        self.setWindowTitle('Beat Bank')
        self.setGeometry(100, 100, 1400, 200)

    def declare_layouts(self):
        print("Creating layouts...")
        self.beatbank_splitter = QSplitter()  # Splitter for sidebar and main
        self.beatbank_layout = QHBoxLayout()
        self.main_layout = QVBoxLayout()
        self.table_layout = QVBoxLayout()
        self.bottom_layout = QHBoxLayout()

    def init_side_bar(self):
        print("creating sidebar...")
        self.sidebar = SideBar(self)
        self.setStyleSheet("""
            QListView {
                background-color: #222; /* Dark background */
                color: #EEE; /* Light text color */
                font: 16px; /* Font size */
                border: none; /* No border around the view */
            }
            QListView::item {
                border: 1px solid #FFFFFF; /* Subtle border for each item */
                border-radius: 6px; /* Slightly rounded corners for the border */
                margin: 2px; /* Margin around items */
                padding: 5px; /* Padding inside items */
            }
            QListView::item:selected {
                background-color: #666; /* Background color of a selected item */
            }
            QListView::item:hover {
                background-color: #555; /* Background color when hovering over an item */
            }
            """)
        self.sidebar_layout = self.sidebar.sidebar_layout

    def init_setupLayouts(self):
        print("Setting up layouts...")
        self.table_layout.addWidget(self.table)

        # Add table and bottom to main layout
        self.main_layout.addLayout(self.table_layout, 80)
        self.main_layout.addLayout(self.bottom_layout, 20)

        self.beatbank_layout.addLayout(self.sidebar_layout, 10)  # sidebar takes up 10% of space
        self.beatbank_layout.addLayout(self.main_layout, 90)  # main takes up 90% of space

        print("Layouts initialized.")

    def finalizeLayout(self):
        self.container = QWidget(self)
        self.container.setLayout(self.beatbank_layout)
        self.setCentralWidget(self.container)

    def init_beat_table(self):
        self.table = BeatTable(self, self.audio_signal)
        self.delegate = InvalidFileDelegate(self.table)
        self.table.setItemDelegate(self.delegate)
        self.table.setModel(self.model_manager.proxyModel)
        self.table.setSortingEnabled(True)
        self.table.verticalHeader().hide()
        self.table.setStyleSheet("""
        QTableView {
            border: 1px solid #444;
            border-radius: 5px;
            background-color: #222;
            color: #EEE;
        }
        QHeaderView::section {
            background-color: #333;
            padding: 5px;
            border: 1px solid #444;
            font-size: 14px;
            color: #FFF;
        }
        QTableView QTableCornerButton::section {
            background: #333;
            border: 1px solid #444.
        }
        """)

    def init_menu_bar(self):
        menubar = InitializeMenuBar(self)
        menubar.init_menu_bar()
