import os

import psycopg2
from psycopg2 import Error

from db.db_settings_data import DbSettingsData


class DbConnection:
    """Подключение к серверу БД"""
    def __init__(self):

        self.db_settings = DbSettingsData()  # type: DbSettingsData
        """создание настроек подключения к БД"""

    def connect(self):
        try:
            """Подключение к экземпляру БД"""
            db_settings = self.db_settings

            print("Устанавливается соединение с БД")
            return psycopg2.connect(
                database=db_settings.database,
                user=db_settings.user,
                password=db_settings.password,
                host=db_settings.host,
                port=db_settings.port
            )

        except (Exception, Error) as error:
            print("Ошибка Подключения к БД", error)

        finally:
            print("Соединение с БД прошло успешно")
