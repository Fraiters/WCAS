import asyncio
from datetime import datetime
from typing import List

from aiogram import Bot
from aiogram.types import ReplyKeyboardRemove

from models.report import Report
from models.task import TASK_STATUS
from reports.db.report_db import ReportDb
from tasks.db.task_db import TaskDb
from user.db.user_db import UserDb
from user.user_settings import ADMINS
from utils.utils import date_time_join


# Задержка для проверки отчета (в секундах - 1800 сек, в минутах - 30 мин)
DELAY_FOR_CHECK = 60 * 30
# Предельное значение составления отчетов для исполнителя (в часах)
LIM_EXECUTOR_HOURS_TIME = 24
# Предельное значение составления отчетов для руководителя (в часах)
LIM_ADMIN_HOURS_TIME = 48


class Notification:

    def __init__(self, bot: Bot):

        self.bot = bot
        # список с id всех выполняющихся задач
        self.doing_tasks_id = ...  # type: List[int]
        self.executor_id = ...
        self.current_date = datetime.now()
        self.last_date = ...  # type: datetime
        self.delta_hours_time = ...  # type: float

    async def check_executor_report(self):
        """ Проверка существования отчета у исполнителя """
        while True:
            task_db = TaskDb()
            doing_tasks_id = await task_db.select_uuid_by_status(status=TASK_STATUS[1])

            await asyncio.sleep(DELAY_FOR_CHECK)

            if doing_tasks_id != []:
                self.doing_tasks_id = [item[0] for item in doing_tasks_id]
                report_db = ReportDb()

                for doing_task_id in self.doing_tasks_id:
                    db_data_reports = await report_db.select_report_by_id_related_task(
                        id_related_task=str(doing_task_id))

                    if db_data_reports == []:
                        author = await task_db.select_executor_id_by_uuid(uuid=doing_task_id)
                        user_db = UserDb()
                        user_id = await user_db.select_user_id_by_username(username=author)
                        await self.bot.send_message(user_id,
                                                    f"Составьте первый отчет о том, "
                                                    f"что начали выполнять задачу с id = {doing_task_id}",
                                                    reply_markup=ReplyKeyboardRemove())
                        continue

                    # начальное значение последней даты
                    last_date = datetime.strptime('01.01.1980 00:00', "%d.%m.%Y %H:%M")
                    for db_data_report in db_data_reports:
                        current_report = Report()
                        current_report.from_tuple(data=db_data_report)
                        current_last_date = date_time_join(date=current_report.date, time=current_report.time)
                        if current_last_date > last_date:
                            last_date = current_last_date
                    # берется любое значение отчета для заполнения id исполнителя
                    report = Report()
                    report.from_tuple(data=db_data_reports[0])
                    self.executor_id = report.author
                    self.last_date = last_date
                    # Разница времени в часах
                    self.delta_hours_time = (self.current_date - self.last_date).total_seconds() // 60 // 60

                    if self.delta_hours_time > LIM_EXECUTOR_HOURS_TIME:
                        user_db = UserDb()
                        user_id = await user_db.select_user_id_by_username(username=self.executor_id)
                        await self.bot.send_message(user_id,
                                                    f"Не забудьте сделать отчет по задаче с id = "
                                                    f"{doing_task_id}",
                                                    reply_markup=ReplyKeyboardRemove())
                    elif self.delta_hours_time > LIM_ADMIN_HOURS_TIME:
                        user_db = UserDb()
                        for admin in ADMINS:
                            user_id = await user_db.select_user_id_by_username(username=admin)
                            await self.bot.send_message(user_id,
                                                        f"Исполнитель @{self.executor_id} не сделал отчет "
                                                        f"по задаче с id = {doing_task_id}",
                                                        reply_markup=ReplyKeyboardRemove())
