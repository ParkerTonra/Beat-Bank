from PyQt6.QtWidgets import QVBoxLayout, QLabel, QLineEdit, QPushButton
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QWidget
import PyQt6.QtWidgets

from controllers import user_settings_controller
from PyQt6.QtWidgets import QMessageBox
from PyQt6 import QtGui
from controllers.user_settings_controller import UserSettingsController


class UserSettingsWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.user_settings_controller = UserSettingsController(self)
        self.initUI()

    def initUI(self):
        print("Initializing UI for user settings window...")
        # Create widgets for label and text entry
        # Default Artist Name (if none found)
        self.default_artist_label = QLabel("Default Artist: ", self)
        self.default_artist_line_edit = QLineEdit(self)
        
        # Submit button
        self.submitButton = QPushButton("Submit", self)

        # Form layout
        layout = QVBoxLayout()
        
        # checkbox for developer mode
        self.developer_mode_checkbox = PyQt6.QtWidgets.QCheckBox("Developer Mode", self)
        self.developer_mode_checkbox.setChecked(self.user_settings_controller.get_developer_mode())
        self.developer_mode_checkbox.stateChanged.connect(self.user_settings_controller.toggle_developer_mode)
        #checkbox for dark mode (TODO)
        
        # Add the widgets to the layout
        layout.addWidget(self.default_artist_label)
        layout.addWidget(self.default_artist_line_edit)
        layout.addWidget(self.developer_mode_checkbox)
        layout.addWidget(self.submitButton)

        # Set the layout on the application's window
        self.setLayout(layout)
        
        # Set the window title
        self.setWindowTitle("User Settings")
        
        # Set the window size
        self.resize(400, 300)
        
        # Center the window
        self.center()
        
        # Set the window icon
        self.setWindowIcon(QIcon('icons/user_settings_icon.png'))
        
        # Show the window
        self.show()
        
    def center(self):
        # Get the application's frame geometry
        qr = self.frameGeometry()
        
        # Get the screen's center point
        cp = QtGui.QGuiApplication.primaryScreen().availableGeometry().center()
        
        # Set the center point of the rectangle to the center of the screen
        qr.moveCenter(cp)
        
        # Move the top-left point of the application window to the top-left point of the qr rectangle
        self.move(qr.topLeft())

            
    #def keyPressEvent(self, event):
        # Override
        #pass