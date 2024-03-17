from typing import Dict, Tuple, Union
from db.base_db import BaseDb
from db.db_settings import DB_REPORTS_COMMANDS


class ReportBaseDb(BaseDb):
    """Класс работы с таблицей 'reports' """

    async def insert_record_report(self, data: Dict):
        """Добавление записи в таблицу отчетов"""
        command = DB_REPORTS_COMMANDS.get("insert_report")
        self.cursor.execute(command, tuple(data.values()))
        self.connection.commit()

    async def select_uuid_by_title(self, title: str) -> int:
        """ Выбор uuid по названию отчета"""
        command = DB_REPORTS_COMMANDS.get("select_uuid_by_title")
        result = await self.select_by(command=command, data=title)  # type: Union[Tuple, None]

        if result is None:
            msg = "uuid по данному title не существует"
            raise Exception(msg)

        return result[0]
