# utils.py
from PyQt6.QtWidgets import QMessageBox, QFileDialog, QDialog, QInputDialog, QLineEdit
from PyQt6.QtCore import QSettings
import subprocess
import os
import pickle
import platform

# -------------------------------------------------------------------------
# Global Utility functions
# -------------------------------------------------------------------------
class Utils:
    @staticmethod
    def show_warning_message(self, title, message):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Icon.Warning)
        msg.setWindowTitle(title)
        msg.setText(message)
        msg.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg.exec()

    @staticmethod
    # Function to save credentials to a file
    def save_credentials(credentials, filename='token.pickle'):
        with open('token.pickle', 'wb') as token:
            pickle.dump(credentials, token)
    
    @staticmethod
    # Function to load credentials from a file
    def load_credentials(filename='token.pickle'):
        if os.path.exists(filename):
            with open(filename, 'rb') as token:
                return pickle.load(token)
        return None

    @staticmethod
    def open_file_location(file_path):
        if not os.path.exists(file_path):
            Utils.show_warning_message("File Not Found", "The file path does not exist.")
            return

        if platform.system() == 'Windows':
            print(f"Opening file location in windows: {file_path}")
            normalized_path = os.path.normpath(file_path)
            subprocess.Popen(f'explorer /select,"{normalized_path}"', shell=True)
        elif platform.system() == 'Darwin':  # macOS
            subprocess.Popen(['open', '-R', file_path])
        else:  # Assuming Linux or other Unix-like OS
            subprocess.Popen(['xdg-open', file_path])

    @staticmethod
    def get_path():
            path, _ = QFileDialog.getOpenFileName("Select Audio File", "", "Audio Files (*.mp3 *.wav *.flac);;All Files (*)")
            return path

    @staticmethod
    def ask_user(title, message):
        text, ok = QInputDialog.getText(None, title, message, QLineEdit.EchoMode.Normal, "")
        if ok:
            return text
        return None