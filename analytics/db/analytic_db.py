from typing import Dict, Tuple, Union, List

from db.base_db import BaseDb
from db.db_settings import DB_ANALYTICS_COMMANDS


class AnalyticDb(BaseDb):
    """ Класс работы с таблицей 'analytics' """

    async def insert_record_analytic(self, data: Dict):
        """ Добавление записи в таблицу аналитиков """
        command = DB_ANALYTICS_COMMANDS.get("insert_analytic")
        await self.insert_record(command=command, data=data)

    async def select_analytic_id(self, analytic_id: str) -> Union[str, None]:
        """ Выбор analytic_id """
        command = DB_ANALYTICS_COMMANDS.get("select_analytic_id")
        result = await self.select_one_by(command=command, data=analytic_id)  # type: Union[Tuple, None]

        if result is None:
            return None

        return result[0]

    async def select_all_analytics(self) -> List[Tuple]:
        """ Выбор всех аналитиков """
        command = DB_ANALYTICS_COMMANDS.get("select_all_analytics")
        result = await self.select_all(command=command)

        return result

    async def delete_analytic(self, analytic_id: str):
        """ Удаление аналитика """
        command = DB_ANALYTICS_COMMANDS.get("delete_analytic")
        await self.delete_record(command=command, data=analytic_id)
