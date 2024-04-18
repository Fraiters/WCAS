from typing import Dict, Union, Tuple, List
import psycopg2
from db.db_connection import DbConnection


class BaseDb:
    """ Класс работы с БД """

    def __init__(self):
        self.connection = DbConnection().connect()  # type: psycopg2.connection
        self.cursor = self.connection.cursor()  # type: psycopg2.cursor

    async def close_connection(self):
        """ Закрытие соединения """
        self.cursor.close()
        self.connection.close()

    async def create_table(self, command: str):
        """ Создание таблицы в БД """
        try:
            self.cursor.execute(command)
            self.connection.commit()
        except psycopg2.Error as error:
            print("Ошибка при работе с БД", error)

    async def insert_record(self, command: str, data: Dict):
        """ Добавление записи в таблицу """
        try:
            self.cursor.execute(command, tuple(data.values()))
            self.connection.commit()
        except psycopg2.Error as error:
            print("Ошибка при работе с БД", error)

    async def select_one_by(self, command: str, data: Union[str, int]) -> Union[Tuple, None]:
        """ Выбор записи из таблицы БД по одному признаку """
        try:
            self.cursor.execute(command, (data,))
            result = self.cursor.fetchone()
            return result
        except psycopg2.Error as error:
            print("Ошибка при работе с БД", error)

    async def select_many_by(self, command: str, data: Union[str, int]) -> Union[List[Tuple], None]:
        """ Выбор всех записей из таблицы БД по одному признаку """
        try:
            self.cursor.execute(command, (data,))
            result = self.cursor.fetchall()
            return result
        except psycopg2.Error as error:
            print("Ошибка при работе с БД", error)

    async def select_all(self, command: str) -> Union[List[Tuple], None]:
        """ Выбор всех записей из таблицы БД """
        try:
            self.cursor.execute(command)
            result = self.cursor.fetchall()
            return result
        except psycopg2.Error as error:
            print("Ошибка при работе с БД", error)

    async def delete_record(self, command: str, data: int):
        """ Удаление записи из таблицы БД """
        try:
            self.cursor.execute(command, (data,))
            self.connection.commit()
        except psycopg2.Error as error:
            print("Ошибка при работе с БД", error)

    async def update_record(self, command: str, data: Dict, uuid: int):
        """ Изменение записи в таблице """
        try:
            data["uuid"] = uuid
            self.cursor.execute(command, tuple(data.values()))
            self.connection.commit()

        except psycopg2.Error as error:
            print("Ошибка при работе с БД", error)
