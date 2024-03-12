import os
from aiogram import Bot
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from general.general_handlers import GeneralHandler
from tasks.handlers.task_handler import TaskHandler


class TelegramBot:
    """Класс для запуска телеграм бота"""
    bot = Bot(token=os.getenv('TOKEN'))
    storage = MemoryStorage()
    dp = Dispatcher(bot=bot, storage=storage)

    def run(self):
        general_handler = GeneralHandler(bot=self.bot)
        task_handler = TaskHandler(bot=self.bot)

        general_handler.registration(dp=self.dp)
        task_handler.registration(dp=self.dp)

        executor.start_polling(dispatcher=self.dp, skip_updates=True)


if __name__ == '__main__':
    telegram_bot = TelegramBot()
    telegram_bot.run()
