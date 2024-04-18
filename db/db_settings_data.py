from typing import *
from db.db_settings import DB_SETTINGS


class DbSettingsData:
    """Данные настроек БД"""
    def __init__(self):
        db_settings = DB_SETTINGS  # type: Dict
        """словарь с данными настроек БД"""

        self.database = db_settings.get("database")  # type: str
        """имя БД"""
        self.user = db_settings.get("user")  # type: str
        """имя пользователя"""
        self.password = db_settings.get("password")  # type: str
        """пароль"""
        self.host = db_settings.get("host")  # type: str
        """хост"""
        self.port = db_settings.get("port")  # type: str
