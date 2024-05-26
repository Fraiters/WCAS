from typing import List

from aiogram import Bot, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.types import Message, ReplyKeyboardRemove
from analytics.analytic import Analytic
from analytics.db.analytic_db import AnalyticDb
from analytics.keyboards.analytic_kb import AnalyticKb
from settings import GENERAL_BUTTONS, ANALYTICS_BUTTONS
from user.db.user_db import UserDb
from user.user_settings import ADMINS


class FsmAnalytic(StatesGroup):
    """ Класс машины состояний для аналитиков """
    analytic_id = State()
    delete_analytic = State()


class AnalyticHandler:
    """ Класс хендлеров для аналитиков """

    def __init__(self, bot: Bot):
        self.bot = bot
        self.analytic_kb = AnalyticKb()
        self.fsm_analytic = FsmAnalytic()
        self.analytic_db = AnalyticDb()
        self.analytic = ...  # type: Analytic

    async def analytics(self, message: Message):
        """ Хендлер для команды 'Аналитики' """

        kb = self.analytic_kb.add(ANALYTICS_BUTTONS.get("analytic"))
        await self.bot.send_message(message.from_user.id, 'Чтобы добавить аналитика нажмите на '
                                                          '"/Добавить_аналитика"\n\n'
                                                          'Чтобы посмотреть всех аналитиков нажмите на '
                                                          '"/Показать_аналитиков"\n\n'
                                                          'Чтобы удалить аналитика нажмите на '
                                                          '"/Удалить_аналитика"\n\n'
                                                          'Для отмены введите команду "/Отмена"', reply_markup=kb)

    async def add_analytic(self, message: Message):
        """ Хендлер для команды 'Добавить аналитика' (Вход в машину состояний) """
        # ограничение на использование хендлера (могут использовать только админы)
        if message.from_user.username.lower() not in ADMINS:
            kb = self.analytic_kb.add(GENERAL_BUTTONS)
            await self.bot.send_message(message.from_user.id, f'Вы не имеете доступ к добавлению аналитика',
                                        reply_markup=kb)
            return

        self.analytic = Analytic()
        await self.fsm_analytic.analytic_id.set()
        kb = self.analytic_kb.add([ANALYTICS_BUTTONS.get("analytic")[-1]])
        await message.reply("Введите id аналитика", reply_markup=kb)

    async def load_analytic_id(self, message: Message, state: FSMContext):
        """ Загрузка id аналитика """
        analytic_id = message.text.lower()

        # для проверки начала работы пользователя в тг-боте
        user_db = UserDb()
        user_id = await user_db.select_user_id_by_username(username=analytic_id)

        # для проверки существует ли аналитик в таблице аналитиков
        existing_analytic = await self.analytic_db.select_analytic_id(analytic_id=analytic_id)

        if user_id is None:
            kb = self.analytic_kb.add([ANALYTICS_BUTTONS.get("analytic")[-1]])
            await message.reply(f'Пользователь с id = @{analytic_id} не начинал работу с ботом\n'
                                'Повторите попытку', reply_markup=kb)
        elif analytic_id == existing_analytic:
            kb = self.analytic_kb.add([ANALYTICS_BUTTONS.get("analytic")[-1]])
            await message.reply(f'Аналитик с id = @{analytic_id} уже существует\n'
                                'Повторите попытку', reply_markup=kb)
        else:
            self.analytic.analytic_id = analytic_id
            db_data_analytic = self.analytic.to_dict()
            await self.analytic_db.insert_record_analytic(data=db_data_analytic)
            await state.finish()
            kb = self.analytic_kb.add(GENERAL_BUTTONS)
            await self.bot.send_message(message.from_user.id, f'Аналитик с id = @{analytic_id} '
                                                              f'успешно добавлен', reply_markup=kb)

    async def show_all_analytics(self, message: Message):
        """ Хендлер для команды 'Показать аналитиков' """
        analytics = await self.analytic_db.select_all_analytics()

        if analytics == []:
            kb = self.analytic_kb.add(GENERAL_BUTTONS)
            await self.bot.send_message(message.from_user.id, f"В системе еще не добавлен ни один аналитик",
                                        reply_markup=kb)
            return

        existing_analytics_id = []  # type: List[str]

        for analytic in analytics:
            for analytic_id in analytic:
                existing_analytics_id.append(analytic_id)

        for existing_analytic_id in existing_analytics_id:
            await self.bot.send_message(message.from_user.id, f'id аналитика: @{existing_analytic_id}',
                                        reply_markup=ReplyKeyboardRemove())

        kb = self.analytic_kb.add(GENERAL_BUTTONS)
        await self.bot.send_message(message.from_user.id, f'Главное меню', reply_markup=kb)

    async def delete_analytic(self, message: Message):
        """ Хендлер для команды 'Удалить аналитика' """
        # ограничение на использование хендлера (могут использовать только админы)
        if message.from_user.username.lower() not in ADMINS:
            kb = self.analytic_kb.add(GENERAL_BUTTONS)
            await self.bot.send_message(message.from_user.id, f'Вы не имеете доступ к удалению аналитика',
                                        reply_markup=kb)
            return

        await self.fsm_analytic.delete_analytic.set()
        kb = self.analytic_kb.add([ANALYTICS_BUTTONS.get("analytic")[-1]])
        await message.reply("Введите id аналитика, которого хотели бы удалить", reply_markup=kb)

    async def cancel(self, message: Message, state: FSMContext):
        """ Выход из машины состояний """
        current_state = await state.get_state()
        if current_state is not None:
            await state.finish()
        kb = self.analytic_kb.add(GENERAL_BUTTONS)
        await self.bot.send_message(message.from_user.id, 'Главное меню', reply_markup=kb)

    async def input_delete_analytic(self, message: Message, state: FSMContext):
        """ Хендлер для ввода id аналитика, которого необходимо удалить """

        analytic_id = message.text.lower()
        existing_analytic = await self.analytic_db.select_analytic_id(analytic_id=analytic_id)

        if existing_analytic is None:
            kb = self.analytic_kb.add([ANALYTICS_BUTTONS.get("analytic")[-1]])
            await message.reply(f'Аналитика с id = {analytic_id} не существует\n'
                                'Повторите попытку', reply_markup=kb)
        else:

            await self.analytic_db.delete_analytic(analytic_id=analytic_id)
            await state.finish()
            kb = self.analytic_kb.add(GENERAL_BUTTONS)
            await self.bot.send_message(message.from_user.id, f'Аналитик с id = {analytic_id} успешно удален',
                                        reply_markup=kb)

    def registration(self, dp: Dispatcher):
        """Регистрация хендлеров для аналитиков"""
        dp.register_message_handler(callback=self.analytics, commands=['Аналитики'])
        dp.register_message_handler(callback=self.add_analytic, commands=['Добавить_аналитика'],
                                    state=None)
        dp.register_message_handler(callback=self.show_all_analytics, commands=['Показать_аналитиков'],
                                    state=None)
        dp.register_message_handler(callback=self.delete_analytic, commands=['Удалить_аналитика'],
                                    state=None)
        dp.register_message_handler(callback=self.cancel, commands=['Отмена'],
                                    state=None)

        # Добавление аналитика
        dp.register_message_handler(callback=self.load_analytic_id,
                                    state=self.fsm_analytic.analytic_id)
        # Удаление аналитика
        dp.register_message_handler(callback=self.input_delete_analytic,
                                    state=self.fsm_analytic.delete_analytic)
