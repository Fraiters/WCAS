from typing import Dict, Tuple, Union, List
from db.base_db import BaseDb
from db.db_settings import DB_REPORTS_COMMANDS


class ReportDb(BaseDb):
    """Класс работы с таблицей 'reports' """

    async def insert_record_report(self, data: Dict):
        """Добавление записи в таблицу отчетов"""
        command = DB_REPORTS_COMMANDS.get("insert_report")
        self.cursor.execute(command, tuple(data.values()))
        self.connection.commit()

    async def select_uuid_by_title(self, title: str) -> Union[int, None]:
        """ Выбор uuid по названию отчета"""
        command = DB_REPORTS_COMMANDS.get("select_uuid_by_title")
        result = await self.select_one_by(command=command, data=title)  # type: Union[Tuple, None]

        if result is None:
            return None
            # msg = "uuid по данному title не существует"
            # raise Exception(msg)

        return result[0]

    async def select_all_reports(self) -> List[Tuple]:
        """ Выбор всех отчетов (их название и id) """
        command = DB_REPORTS_COMMANDS.get("select_all_reports")
        result = await self.select_all(command=command)

        if result == []:
            msg = "Таблица reports - пустая"
            raise Exception(msg)

        return result

    async def select_report_by_user_id(self, user_id: str) -> List[Tuple]:
        """ Выбор отчета по id автора отчета """
        command = DB_REPORTS_COMMANDS.get("select_report_by_user_id")
        result = await self.select_many_by(command=command, data=user_id)
        return result

    async def select_report_by_uuid(self, uuid: int) -> Union[Tuple, None]:
        """ Выбор отчета по uuid отчета """
        command = DB_REPORTS_COMMANDS.get("select_report_by_uuid")
        result = await self.select_one_by(command=command, data=uuid)
        return result

    async def delete_report(self, uuid: int):
        """ Удаление отчета """
        command = DB_REPORTS_COMMANDS.get("delete_report")
        await self.delete_record(command=command, data=uuid)

    async def update_report(self, data: Dict, uuid: int):
        """ Обновление записи в таблице отчетов """
        command = DB_REPORTS_COMMANDS.get("update_report")
        await self.update_record(command=command, data=data, uuid=uuid)
