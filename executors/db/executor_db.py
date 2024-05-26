from typing import Dict, Tuple, Union, List

from db.base_db import BaseDb
from db.db_settings import DB_EXECUTORS_COMMANDS


class ExecutorDb(BaseDb):
    """ Класс работы с таблицей 'executors' """

    async def insert_record_executor(self, data: Dict):
        """ Добавление записи в таблицу исполнителей """
        command = DB_EXECUTORS_COMMANDS.get("insert_executor")
        await self.insert_record(command=command, data=data)

    async def select_executor_id(self, executor_id: str) -> Union[str, None]:
        """ Выбор executor_id """
        command = DB_EXECUTORS_COMMANDS.get("select_executor_id")
        result = await self.select_one_by(command=command, data=executor_id)  # type: Union[Tuple, None]

        if result is None:
            return None

        return result[0]

    async def select_all_executors(self) -> List[Tuple]:
        """ Выбор всех исполнителей """
        command = DB_EXECUTORS_COMMANDS.get("select_all_executors")
        result = await self.select_all(command=command)

        return result

    async def delete_executor(self, executor_id: str):
        """ Удаление исполнителя """
        command = DB_EXECUTORS_COMMANDS.get("delete_executor")
        await self.delete_record(command=command, data=executor_id)
