import sqlite3
from sqlite3 import Cursor
from sqlite3 import Connection
from typing import Dict, Union, Tuple


class BaseDb:
    """ Класс работы с БД """

    def __init__(self, db_name: str):
        self.db_name = db_name
        self.connection = sqlite3.connect(self.db_name)  # type: Connection
        self.cursor = self.connection.cursor()  # type: Cursor

    async def create_table(self, command: str):
        """ Создание таблицы в БД """
        self.connection.execute(command)
        self.connection.commit()

    async def insert_record(self, command: str, data: Dict):
        """ Добавление записи в таблицу """
        self.cursor.execute(command, tuple(data.values()))
        self.connection.commit()

    async def select_by(self, command: str, data: Union[str, int]) -> Union[Tuple, None]:
        """ Выбор записи из таблицы БД по одному признаку """
        self.cursor.execute(command, (data,))
        result = self.cursor.fetchone()
        return result
