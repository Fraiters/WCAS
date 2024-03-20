import sqlite3
from sqlite3 import Cursor
from sqlite3 import Connection
from typing import Dict, Union, Tuple, List


class BaseDb:
    """ Класс работы с БД """

    def __init__(self, db_name: str):
        self.db_name = db_name
        self.connection = sqlite3.connect(self.db_name)  # type: Connection
        self.cursor = self.connection.cursor()  # type: Cursor

    async def close_connection(self):
        """ Закрытие соединения """
        self.connection.close()

    async def create_table(self, command: str):
        """ Создание таблицы в БД """
        try:
            self.connection.execute(command)
            self.connection.commit()
        except sqlite3.Error as error:
            print("Ошибка при работе с SQLite", error)

    async def insert_record(self, command: str, data: Dict):
        """ Добавление записи в таблицу """
        try:
            self.cursor.execute(command, tuple(data.values()))
            self.connection.commit()
        except sqlite3.Error as error:
            print("Ошибка при работе с SQLite", error)

    async def select_one_by(self, command: str, data: Union[str, int]) -> Union[Tuple, None]:
        """ Выбор записи из таблицы БД по одному признаку """
        try:
            self.cursor.execute(command, (data,))
            result = self.cursor.fetchone()
            return result
        except sqlite3.Error as error:
            print("Ошибка при работе с SQLite", error)

    async def select_many_by(self, command: str, data: Union[str, int]) -> Union[List[Tuple], None]:
        """ Выбор всех записей из таблицы БД по одному признаку """
        try:
            self.cursor.execute(command, (data,))
            result = self.cursor.fetchall()
            return result
        except sqlite3.Error as error:
            print("Ошибка при работе с SQLite", error)

    async def select_all(self, command: str) -> Union[List[Tuple], None]:
        """ Выбор всех записей из таблицы БД """
        try:
            self.cursor.execute(command)
            result = self.cursor.fetchall()
            return result
        except sqlite3.Error as error:
            print("Ошибка при работе с SQLite", error)

    async def delete_record(self, command: str, data: int):
        """ Удаление записи из таблицы БД """
        try:
            self.cursor.execute(command, (data,))
            self.connection.commit()
        except sqlite3.Error as error:
            print("Ошибка при работе с SQLite", error)

    async def update_record(self, command: str, data: Dict, uuid: int):
        """ Изменение записи в таблице """
        try:
            data["uuid"] = uuid
            self.cursor.execute(command, tuple(data.values()))
            self.connection.commit()

        except sqlite3.Error as error:
            print("Ошибка при работе с SQLite", error)
