from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from utilities.util import Utils
from PyQt6.QtWidgets import QInputDialog
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import webbrowser
import threading
import webbrowser
import os

class GoogleDriveIntegration:
    def __init__(self, gdrive_service=None):
        #if setting "gdrive_toggle" is false, don't initialize gdrive. Otherwise, proceed.
        settings = Utils.load_settings()
        if settings.value("gdrive_toggle") == False:
            print("Google Drive integration is disabled. Skipping initialization.")
            return
        self.gdrive_service = gdrive_service
        if self.gdrive_service is None:
            self.init_google_drive()
    
    def show_folder_selection(self):
        folder_names = self.list_and_choose_folder()
        print(folder_names)
        dialog = QInputDialog()
        dialog.setWindowTitle("Choose Folder")
        dialog.setLabelText("Select the folder to store your Beat Bank files:")
        dialog.setComboBoxItems(folder_names)
        dialog.setComboBoxEditable(False)
        ok = dialog.exec()
        return dialog.comboBoxItems().index(dialog.textValue()), ok
        
    def toggle_gdrive(self):
        settings = Utils.load_settings()
        if settings.value("gdrive_toggle") == False:
            settings.setValue("gdrive_toggle", True)
            self.__init__()
        else:
            settings.setValue("gdrive_toggle", False)
            self.gdrive_service = None
        Utils.save_settings(settings)
    
    def init_google_drive(self):
        
        print("Checking for existing Google Drive credentials...")
        credentials = Utils.load_credentials()
        print(f"Credentials: {credentials}")
        if credentials and credentials.valid:
            print("Credentials loaded.")
        elif credentials and credentials.expired and credentials.refresh_token:
            print("Refreshing credentials...")
            try:
                credentials.refresh(Request())
                Utils.save_credentials(credentials)  # Make sure to save the refreshed credentials
                print("Credentials refreshed and saved.")
            except Exception as e:
                print(f"Error refreshing credentials: {e}")
                return
        else:
            print("No valid credentials available.")
            return

        self.gdrive_service = build('drive', 'v3', credentials=credentials)
    
    def authenticate_user(self):
        if hasattr(self, 'gdrive_service'):
            print("User already authenticated.")
            return
        
        print("Authenticating user...")
        # Define the scopes your application requires
        SCOPES = ['https://www.googleapis.com/auth/drive']
        
        
        secret_path = os.path.join(os.path.dirname(__file__), '..','client_secrets.json')
        secret_path = os.path.abspath(secret_path)
        
        
        # Start the flow using the client secrets file you downloaded from the Google Developer Console
        flow = InstalledAppFlow.from_client_secrets_file(secret_path, SCOPES)
        
        # This will open the default web browser for the user to log in
        # After logging in, the user will be prompted to give your application access to their Google Drive
        auth_url, _ = flow.authorization_url(prompt='consent')
        
        webbrowser.open(auth_url)
        
        # Once authorized, exchange the authorization code for tokens
        flow.run_local_server(port=0)
        
        # Now you have credentials, you can create a service object to interact with the Drive API
        credentials = flow.credentials
        Utils.save_credentials(credentials)
        print("User authenticated. Saving credentials...")
        # Use these credentials to access Google Drive, for example
        self.gdrive_service = build('drive', 'v3', credentials=credentials)
        print("Service object created.")
    
    def find_or_create_beatbank_folder(self, folder_name):
        if not hasattr(self, 'gdrive_service'):
            print("User not authenticated.")
            return
        service = self.gdrive_service
        # Search for the folder by name
        folder_name = Utils.ask_user("Beat Bank folder", "Enter the name of the folder to store your Beat Bank files.")
        if folder_name:
            print(f"Folder: {folder_name}")
        else:
            print("No answer was entered or dialog was canceled.")
            return
        query = f"mimeType='application/vnd.google-apps.folder' and name='{folder_name}' and trashed=false"
        response = service.files().list(q=query,
                                        spaces='drive',
                                        fields='files(id, name)').execute()
        
        folders = response.get('files', [])

        # If the folder exists, return its ID
        if folders:
            return folders[0]['id']  # Assuming the first match is the one you want

        # If the folder doesn't exist, create it
        folder_metadata = {
            'name': folder_name,
            'mimeType': 'application/vnd.google-apps.folder'
        }
        folder = service.files().create(body=folder_metadata, fields='id').execute()
        return folder.get('id')
    
    def list_and_choose_folder(self):
        if not hasattr(self, 'gdrive_service') or self.gdrive_service is None:
            print("User not authenticated / service not initialized.")
            return []

        service = self.gdrive_service
        # Query to list folders
        query = "mimeType='application/vnd.google-apps.folder' and trashed=false"
        response = service.files().list(q=query,
                                        spaces='drive',
                                        fields='files(id, name)',
                                        pageSize=100).execute()  # Adjust pageSize as needed
        
        folders = response.get('files', [])

        # Check if there are folders
        if not folders:
            print("No folders found.")
            return

        # Create a dialog or use a custom method to display folders and let the user choose
        folder_names = [folder['name'] for folder in folders]
        return folder_names