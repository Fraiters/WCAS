from typing import List, Tuple, Dict, Union

from db.base_db import BaseDb
from db.db_settings import DB_EXECUTORS_RATING_COMMANDS


class ExecutorRatingDb(BaseDb):
    """ Класс работы с таблицей 'executor_rating' """

    async def insert_record_executor(self, data: Dict):
        """ Добавление записи в таблицу рейтинга исполнителей """
        command = DB_EXECUTORS_RATING_COMMANDS.get("insert_executor")
        await self.insert_record(command=command, data=data)

    async def select_performance_indicator_by_executor_id(self, executor_id: str) -> Union[Tuple, None]:
        """ Выбор показателя эффективности по id исполнителя """
        command = DB_EXECUTORS_RATING_COMMANDS.get("select_performance_indicator_by_executor_id")
        result = await self.select_one_by(command=command, data=executor_id)
        return result

    async def select_all_executors_order_by_pi(self) -> List[Tuple]:
        """ Выбор всех строк рейтинга исполнителей (id исполнителя, показателя эффективности) """
        command = DB_EXECUTORS_RATING_COMMANDS.get("select_all_executors_order_by_pi")
        result = await self.select_all(command=command)

        return result

    async def update_performance_indicator_executor(self, data: Dict):
        """ Обновление записи в таблице рейтинга исполнителей """
        command = DB_EXECUTORS_RATING_COMMANDS.get("update_performance_indicator")
        await self.update_record(command=command, data=data)

    async def delete_executor(self, executor_id: str):
        """ Удаление исполнителя из рейтинга """
        command = DB_EXECUTORS_RATING_COMMANDS.get("delete_executor")
        await self.delete_record(command=command, data=executor_id)
