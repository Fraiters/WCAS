from aiogram import Bot, Dispatcher
from aiogram.types import Message
from settings import GENERAL_BUTTONS
from general.general_keyboard import GeneralKb
from user.user import User
from user.user_db import UserDb


class GeneralHandler:
    """Класс главных хендлеров"""

    def __init__(self, bot: Bot):
        self.bot = bot
        self.general_kb = GeneralKb()
        self.user_db = UserDb()

    async def commands_start(self, message: Message):
        """Хендлер для команд 'start', 'help' """
        try:
            kb = self.general_kb.add(GENERAL_BUTTONS)
            await self.bot.send_message(message.from_user.id, 'С вами бот для контроля и учета работы',
                                        reply_markup=kb)

            if message.from_user.username is None:
                await message.reply('У вас не задано имя пользователя, \n'
                                    'Для работы с ботом необходимо его создать')
                return

            username = str(message.from_user.username).lower()
            user_id = message.from_user.id

            # Исключение на создание пользователя с не уникальным username
            uuid_user = await self.user_db.select_uuid_by_username(username=username)
            if uuid_user is None:
                user = User(username=username, user_id=user_id)
                db_user_data = user.to_dict()
                await self.user_db.insert_record_user(data=db_user_data)

        except:
            await message.reply('Общение с ботом через лс, пожалуйста напишите ему: \n @work_control_accounting_bot')

    def registration(self, dp: Dispatcher):
        """Регистрация главных хендлеров"""
        dp.register_message_handler(callback=self.commands_start, commands=['start', 'help'])
