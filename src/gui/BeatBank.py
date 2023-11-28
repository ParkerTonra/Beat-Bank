from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtSql import QSqlTableModel
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QTableWidget, QTableWidgetItem, QVBoxLayout, 
    QWidget, QLabel, QFileDialog, QHeaderView, QMessageBox, QHBoxLayout, QFrame,
    QPushButton, QAbstractItemView, QTableView, QAbstractScrollArea, QMenu
)
from PyQt6.QtCore import Qt, QUrl, QMimeData, QTime, QEvent
from controllers import database_controller, track_controller
from database import SessionLocal, init_db
from business.track_business_model import TrackBusinessModel
from models.track import Track
from models.version import Version
from controllers.track_controller import TrackController
from gui.edit_track_window import EditTrackWindow
import mutagen
import os
import time
from models.user_settings import UserSettings
from controllers.database_controller import DatabaseManager

# BeatBank.py (root)/src/gui/BeatBank.py

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.controller = DatabaseManager(self)
        self._updating_cell = False
        self.isEditing = False
        self.init_ui()

    def init_ui(self):
        # Initialize UI components...
        print("Initializing UI for main window...")
        self.setWindowTitle('Beat Bank')
        self.setGeometry(100, 100, 1400, 200)
        
        # Double click interval
        self.lastClickTime = QTime()
        self.doubleClickInterval = QtWidgets.QApplication.doubleClickInterval()
        
        # Define layouts 
        left_layout = QVBoxLayout()
        right_layout = QVBoxLayout()
        top_layout = QHBoxLayout()
        table_layout = QVBoxLayout()
        main_layout = QVBoxLayout()
        
        
        
        # -----------------------------------------------------------------------------
        # LEFT COLUMN LAYOUT
        # ----------------------------------------------------------------------------- 

        # Refresh button
        self.refresh_button = QPushButton('Refresh', self)
        self.refresh_button.clicked.connect(self.table_refresh)
        self.refresh_button.setIcon(QtGui.QIcon('src/assets/pictures/refresh.png'))
        
        
        
        
        # Create a table view widget for the filtered tracks table
        self.filteredTableView = QTableView(self)
        self.filteredTableView.setFrameStyle(QFrame.Shape.Panel | QFrame.Shadow.Sunken)
        # make the table have 2 columns: title and bpm
        # users can select how they want data to be displayed
        # users can select which columns to display
        #users can toggle this table on and off
        #users can select which columns to display
        
        
        
        left_layout.addWidget(self.refresh_button)
        # TODO: left_layout.addWidget(self.filteredTableView)
        # -----------------------------------------------------------------------------
        # RIGHT COLUMN LAYOUT
        # -----------------------------------------------------------------------------    

        # 'Add Track' Button
        self.add_button = QPushButton('Add track', self)
        self.add_button.clicked.connect(self.add_track)
        right_layout.addWidget(self.add_button)
        
        # 'Delete Track' Button
        self.delete_button = QPushButton('Delete track', self)
        self.delete_button.clicked.connect(self.delete_track)
        right_layout.addWidget(self.delete_button)
        
        # 'Edit Track' Button
        self.edit_button = QPushButton('Edit track', self)
        self.edit_button.clicked.connect(self.edit_track)
        right_layout.addWidget(self.edit_button)
        
        # 'Settings' Button
        self.edit_button = QPushButton('Settings', self)
        self.edit_button.clicked.connect(self.open_settings)
        right_layout.addWidget(self.edit_button)
        
        # -----------------------------------------------------------------------------
        # TOP COLUMN LAYOUT (R/L)
        # ----------------------------------------------------------------------------- 
        
        top_layout.addLayout(left_layout)
        top_layout.addLayout(right_layout)
        
        # -----------------------------------------------------------------------------
        # TABLE LAYOUT FOR DATABASE
        # -----------------------------------------------------------------------------
        
        # Create a table view widget for the tracks table
        self.table = QTableView(self)
        self.table.setMinimumHeight(500)
        
        # Drag and drop (TODO)
        self.table.setAcceptDrops(True)
        self.table.setDragEnabled(True)
        
        # Set up QSqlTableModel
        self.model = QSqlTableModel(self)
        self.model.setTable('tracks')
        self.model.setEditStrategy(QSqlTableModel.EditStrategy.OnFieldChange)
        self.model.select()
    
        # Set the model on the table view
        self.table.setModel(self.model)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        table_layout.addWidget(self.table)
        # -----------------------------------------------------------------------------
        # MAIN LAYOUT
        # -----------------------------------------------------------------------------

        
        main_layout.addLayout(top_layout)
        main_layout.addLayout(table_layout)

        # Create a container widget to hold the layout
        self.container = QWidget(self)
        self.container.setLayout(main_layout)

        self.setCentralWidget(self.container)
        
        # Populate the model
        self.model.select()
    
# =============================================================================
# MAIN WINDOW FUNCTIONS
# =============================================================================    

    # -------------------------------------------------------------------------
    # FUNCTIONS LINKED TO BUTTONS
    # -------------------------------------------------------------------------
    def add_track(self):
        #QFiledialog to select a file
        pass
    def delete_track(self):
        #ask users "are you sure you want to delete this track?
        # if yes, delete the track"
        pass
    def edit_track(self):
        # replace the file with a new file.
        pass
    def open_settings(self):
        # open the settings window
        pass
    
    # -----------------------------------------------------------------------------
    # FUNCTIONS LINKED TO TABLE
    # -----------------------------------------------------------------------------
    
    def table_refresh(self):
        # Refresh the table
        self.model.select()
        pass
    
    def update_table_row(self, track_id):
        # Update a row in the table
        pass