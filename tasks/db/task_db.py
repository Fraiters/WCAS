from typing import Dict, Tuple, Union, List

from db.base_db import BaseDb
from db.db_settings import DB_TASKS_COMMANDS


class TaskDb(BaseDb):
    """ Класс работы с таблицей 'tasks' """

    async def insert_record_task(self, data: Dict):
        """ Добавление записи в таблицу задач """
        command = DB_TASKS_COMMANDS.get("insert_task")
        await self.insert_record(command=command, data=data)

    async def select_uuid_by_title(self, title: str) -> Union[int, None]:
        """ Выбор uuid по названию задачи"""
        command = DB_TASKS_COMMANDS.get("select_uuid_by_title")
        result = await self.select_one_by(command=command, data=title)  # type: Union[Tuple, None]

        if result is None:
            return None
            # msg = "uuid по данному title не существует"
            # raise Exception(msg)

        return result[0]

    async def select_title_by_uuid(self, uuid: int) -> Union[Tuple, None]:
        """ Выбор названия задачи по uuid"""
        command = DB_TASKS_COMMANDS.get("select_title_by_uuid")
        result = await self.select_one_by(command=command, data=uuid)  # type: Union[Tuple, None]
        return result

    async def select_all_tasks(self) -> List[Tuple]:
        """ Выбор всех задач (их название и id) """
        command = DB_TASKS_COMMANDS.get("select_all_tasks")
        result = await self.select_all(command=command)

        if result == []:
            msg = "Таблица tasks - пустая"
            raise Exception(msg)

        return result

    async def select_task_by_executor_id(self, executor_id: str) -> List[Tuple]:
        """ Выбор задачи по id исполнителя задачи """
        command = DB_TASKS_COMMANDS.get("select_task_by_executor_id")
        result = await self.select_many_by(command=command, data=executor_id)
        return result

    async def select_task_by_uuid(self, uuid: int) -> Union[Tuple, None]:
        """ Выбор задачи по уникальному id """
        command = DB_TASKS_COMMANDS.get("select_task_by_uuid")
        result = await self.select_one_by(command=command, data=uuid)
        return result

    async def delete_task(self, uuid: int):
        """ Удаление задачи """
        command = DB_TASKS_COMMANDS.get("delete_task")
        await self.delete_record(command=command, data=uuid)

    async def update_task_by_uuid(self, data: Dict, uuid: int):
        """ Обновление записи в таблице задач """
        data["uuid"] = uuid
        command = DB_TASKS_COMMANDS.get("update_task")
        await self.update_record(command=command, data=data)
