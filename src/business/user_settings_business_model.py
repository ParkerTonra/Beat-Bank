

from database import SessionLocal
from models.user_settings import UserSettings


class UserSettingsBusinessModel:
    def get_developer_mode(self):
        with SessionLocal() as session:
            settings = session.query(UserSettings).first()
            if settings is not None:
                return settings.developer_mode
            else:
                # If no settings are found, return a default value (e.g., False)
                return False
        
    def toggle_developer_mode(self):
        with SessionLocal() as session:
            settings = session.query(UserSettings).first()
            if settings is None:
                settings = UserSettings()
                settings.developer_mode = False
                session.add(settings)
            if settings.developer_mode is not None:
                settings.developer_mode = not settings.developer_mode
            else:
                settings.developer_mode = False
            session.commit()
            return settings.developer_mode