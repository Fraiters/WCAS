import os
from aiogram import Bot
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from db.base_db import BaseDb
from db.db_settings import DB_TASKS_COMMANDS, DB_REPORTS_COMMANDS, DB_USERS_COMMANDS, DB_EXECUTORS_RATING_COMMANDS
from general.general_handler import GeneralHandler
from general.unknown_handler import UnknownHandler
from reports.handlers.report_handler import ReportHandler
from tasks.handlers.task_handler import TaskHandler


class TelegramBot:
    """Класс для запуска телеграм бота"""
    bot = Bot(token=os.getenv('TOKEN'))
    storage = MemoryStorage()
    dp = Dispatcher(bot=bot, storage=storage)
    db = BaseDb()

    async def on_startup(self, _):
        await self.db.create_table(command=DB_TASKS_COMMANDS.get('create_task_table'))
        await self.db.create_table(command=DB_REPORTS_COMMANDS.get('create_report_table'))
        await self.db.create_table(command=DB_USERS_COMMANDS.get('create_user_table'))
        await self.db.create_table(command=DB_EXECUTORS_RATING_COMMANDS.get('create_executor_rating_table'))
        await self.db.close_connection()

    def run(self):
        general_handler = GeneralHandler(bot=self.bot)
        task_handler = TaskHandler(bot=self.bot)
        report_handler = ReportHandler(bot=self.bot)
        unknown_handler = UnknownHandler(bot=self.bot)

        general_handler.registration(dp=self.dp)
        task_handler.registration(dp=self.dp)
        report_handler.registration(dp=self.dp)
        unknown_handler.registration(dp=self.dp)

        executor.start_polling(dispatcher=self.dp, skip_updates=True, on_startup=self.on_startup)


if __name__ == '__main__':

    telegram_bot = TelegramBot()
    telegram_bot.run()
