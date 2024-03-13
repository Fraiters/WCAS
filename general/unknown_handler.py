from aiogram import Bot, Dispatcher
from aiogram.types import Message
from settings import GENERAL_BUTTONS


class UnknownHandler:
    """Класс неизвестных хендлеров"""

    def __init__(self, bot: Bot, ):  # db: Db):
        self.bot = bot

    async def unknown_commands(self, message: Message):
        """Хендлер для неизвестных начальных команд (все кроме 'start', 'help' ...) """
        if message.text in GENERAL_BUTTONS:
            pass
        else:
            await self.bot.send_message(message.from_user.id, 'Такой команды не существует! \n'
                                        'Для получения информации о существующих командах введите /help')
            await message.delete()

    def registration(self, dp: Dispatcher):
        """Регистрация неизвестных хендлеров"""
        dp.register_message_handler(callback=self.unknown_commands)
