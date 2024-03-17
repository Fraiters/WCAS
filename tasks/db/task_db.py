from typing import Dict, Tuple, Union

from db.base_db import BaseDb
from db.db_settings import DB_TASKS_COMMANDS


class TaskBaseDb(BaseDb):
    """ Класс работы с таблицей 'tasks' """

    async def insert_record_task(self, data: Dict):
        """ Добавление записи в таблицу задач """
        command = DB_TASKS_COMMANDS.get("insert_task")
        await self.insert_record(command=command, data=data)

    async def select_uuid_by_title(self, title: str) -> int:
        """ Выбор uuid по названию задачи"""
        command = DB_TASKS_COMMANDS.get("select_uuid_by_title")
        result = await self.select_by(command=command, data=title)  # type: Union[Tuple, None]

        if result is None:
            msg = "uuid по данному title не существует"
            raise Exception(msg)

        return result[0]

    async def select_title_by_uuid(self, uuid: int) -> Union[Tuple, None]:
        """ Выбор названия задачи по uuid"""
        command = DB_TASKS_COMMANDS.get("select_title_by_uuid")
        result = await self.select_by(command=command, data=uuid)  # type: Union[Tuple, None]

        return result
