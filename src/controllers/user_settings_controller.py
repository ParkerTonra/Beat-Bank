from models.user_settings_business_model import UserSettingsBusinessModel

class UserSettingsController:
    def __init__(self, view):
        super().__init__()
        self.model = UserSettingsBusinessModel()
        self.view = view
        
    def get_developer_mode(self):
        return self.model.get_developer_mode()
    
    def toggle_developer_mode(self):
        self.model.toggle_developer_mode()
        return
    