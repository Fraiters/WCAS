from typing import List, Tuple

from aiogram import Dispatcher, Bot
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.types import Message, ReplyKeyboardRemove

from executor_rating.db.executor_rating_db import ExecutorRatingDb
from executor_rating.executor_rating import ExecutorRating
from executor_rating.keyboards.executor_rating_kb import ExecutorRatingKb
from settings import EXECUTOR_RATING_BUTTONS, GENERAL_BUTTONS
from utils.utils import text_table_layout


class FsmExecutorRating(StatesGroup):
    """ Класс машины состояний для рейтинга """
    delete_executor = State()


class ExecutorRatingHandler:
    """ Класс хендлеров для рейтинга """

    def __init__(self, bot: Bot):
        self.bot = bot
        self.executor_rating_kb = ExecutorRatingKb()
        self.fsm_executor_rating = FsmExecutorRating()
        self.executor_rating_db = ExecutorRatingDb()
        self.executor_rating = ...  # type: ExecutorRating

    # Уровень клавиатуры 1
    # /Показать_рейтинг, /Обнулить_рейтинг, /Удалить_исполнителя_из_рейтинга
    async def executors_rating(self, message: Message):
        """ Хендлер для команды 'Рейтинг' """
        kb = self.executor_rating_kb.add(EXECUTOR_RATING_BUTTONS.get("executor_rating"))
        await self.bot.send_message(message.from_user.id, 'Чтобы посмотреть рейтинг нажмите на "/Показать_рейтинг"\n\n'
                                                          'Чтобы удалить исполнителя из рейтинга нажмите на '
                                                          '"/Удалить_исполнителя_из_рейтинга"\n\n'
                                                          'Для отмены введите команду "/Отмена"', reply_markup=kb)

    # Уровень клавиатуры 2
    # Показать рейтинг:
    async def show_executor_rating(self, message: Message):
        """ Хендлер для команды 'Показать рейтинг' """
        db_executor_rating = await self.executor_rating_db.select_all_executors_order_by_pi()  # type: List[Tuple]

        if db_executor_rating == []:
            kb = self.executor_rating_kb.add(GENERAL_BUTTONS)
            await self.bot.send_message(message.from_user.id,
                                        f"Рейтинг не сформирован т.к. еще никто не закрыл задачу",
                                        reply_markup=kb)
            return

        data = []
        # перевод всех элементов в str
        for line in db_executor_rating:
            data_item = list(line)
            for i in range(len(line)):
                data_item[i] = str(line[i])
            data.append(data_item)

        columns = ["Исполнитель", "Оценка"]

        executor_rating_table = text_table_layout(data=data, columns=columns)

        await self.bot.send_message(message.from_user.id, executor_rating_table, reply_markup=ReplyKeyboardRemove())

        kb = self.executor_rating_kb.add(GENERAL_BUTTONS)
        await self.bot.send_message(message.from_user.id, 'Главное меню', reply_markup=kb)

    # Уровень клавиатуры 2
    # Удалить исполнителя:
    async def input_delete_executor(self, message: Message):
        """ Хендлер для ввода id исполнителя для удаления задачи """
        await self.fsm_executor_rating.delete_executor.set()
        kb = self.executor_rating_kb.add([EXECUTOR_RATING_BUTTONS.get("executor_rating")[-1]])
        await message.reply("Введите id исполнителя, которого хотели бы убрать с рейтинга",
                            reply_markup=kb)

    async def cancel(self, message: Message, state: FSMContext):
        """ Выход из машины состояний """
        current_state = await state.get_state()
        if current_state is not None:
            await state.finish()
        kb = self.executor_rating_kb.add(GENERAL_BUTTONS)
        await self.bot.send_message(message.from_user.id, 'Главное меню', reply_markup=kb)

    async def delete_executor(self, message: Message, state: FSMContext):
        """ Хендлер для команды 'Удалить исполнителя' """

        executor_id = message.text
        db_executor = await self.executor_rating_db.select_performance_indicator_by_executor_id(
            executor_id=executor_id)
        if db_executor is None:
            kb = self.executor_rating_kb.add([EXECUTOR_RATING_BUTTONS.get("executor_rating")[-1]])
            await message.reply(f'Исполнителя с id = {executor_id} не существует\n'
                                'Повторите попытку', reply_markup=kb)
        else:
            await self.executor_rating_db.delete_executor(executor_id=executor_id)
            await state.finish()
            kb = self.executor_rating_kb.add(GENERAL_BUTTONS)
            await self.bot.send_message(message.from_user.id, f'Исполнитель с id = {executor_id} успешно удален',
                                        reply_markup=kb)

    def registration(self, dp: Dispatcher):
        """Регистрация хендлеров для рейтинга исполнителей"""
        dp.register_message_handler(callback=self.executors_rating, commands=['Рейтинг'])

        dp.register_message_handler(callback=self.show_executor_rating, commands=['Показать_рейтинг'],
                                    state=None)
        dp.register_message_handler(callback=self.input_delete_executor, commands=['Удалить_исполнителя_из_рейтинга'],
                                    state=None)
        dp.register_message_handler(callback=self.cancel, commands=['Отмена'],
                                    state='*')
        dp.register_message_handler(self.cancel, Text(equals='Отмена', ignore_case=True),
                                    state='*')

        dp.register_message_handler(callback=self.delete_executor,
                                    state=self.fsm_executor_rating.delete_executor)
