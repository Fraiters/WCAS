from typing import List

from aiogram import Bot, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.types import Message, ReplyKeyboardRemove

from executors.db.executor_db import ExecutorDb
from executors.executor import Executor
from executors.keyboards.executor_kb import ExecutorKb
from models.task import Task, TASK_STATUS
from settings import EXECUTOR_BUTTONS, GENERAL_BUTTONS
from tasks.db.task_db import TaskDb
from user.db.user_db import UserDb
from user.user_settings import ADMINS


class FsmExecutor(StatesGroup):
    """ Класс машины состояний для исполнителей """
    executor_id = State()
    delete_executor = State()


class ExecutorHandler:
    """ Класс хендлеров для исполнителей """

    def __init__(self, bot: Bot):
        self.bot = bot
        self.executor_kb = ExecutorKb()
        self.fsm_executor = FsmExecutor()
        self.executor_db = ExecutorDb()
        self.executor = ...  # type: Executor

    async def executors(self, message: Message):
        """ Хендлер для команды 'Исполнители' """

        kb = self.executor_kb.add(EXECUTOR_BUTTONS.get("executor"))
        await self.bot.send_message(message.from_user.id, 'Чтобы добавить исполнителя нажмите на '
                                                          '"/Добавить_исполнителя"\n\n'
                                                          'Чтобы посмотреть всех исполнителей нажмите на '
                                                          '"/Показать_исполнителей"\n\n'
                                                          'Чтобы удалить исполнителя нажмите на '
                                                          '"/Удалить_исполнителя"\n\n'
                                                          'Для отмены введите команду "/Отмена"', reply_markup=kb)

    async def add_executor(self, message: Message):
        """ Хендлер для команды 'Добавить исполнителя' (Вход в машину состояний) """
        # ограничение на использование хендлера (могут использовать только админы)
        if message.from_user.username.lower() not in ADMINS:
            kb = self.executor_kb.add(GENERAL_BUTTONS)
            await self.bot.send_message(message.from_user.id, f'Вы не имеете доступ к добавлению исполнителя',
                                        reply_markup=kb)
            return

        self.executor = Executor()
        await self.fsm_executor.executor_id.set()
        kb = self.executor_kb.add([EXECUTOR_BUTTONS.get("executor")[-1]])
        await message.reply("Введите id исполнителя", reply_markup=kb)

    async def load_executor_id(self, message: Message, state: FSMContext):
        """ Загрузка id исполнителя """
        executor_id = message.text.lower()

        # для проверки начала работы пользователя в тг-боте
        user_db = UserDb()
        user_id = await user_db.select_user_id_by_username(username=executor_id)

        # для проверки существует ли исполнитель в таблице исполнителей
        existing_executor = await self.executor_db.select_executor_id(executor_id=executor_id)

        if user_id is None:
            kb = self.executor_kb.add([EXECUTOR_BUTTONS.get("executor")[-1]])
            await message.reply(f'Пользователь с id = @{executor_id} не начинал работу с ботом\n'
                                'Повторите попытку', reply_markup=kb)
        elif executor_id == existing_executor:
            kb = self.executor_kb.add([EXECUTOR_BUTTONS.get("executor")[-1]])
            await message.reply(f'Исполнитель с id = @{executor_id} уже существует\n'
                                'Повторите попытку', reply_markup=kb)
        else:
            self.executor.executor_id = executor_id
            db_data_executor = self.executor.to_dict()
            await self.executor_db.insert_record_executor(data=db_data_executor)
            await state.finish()
            kb = self.executor_kb.add(GENERAL_BUTTONS)
            await self.bot.send_message(message.from_user.id, f'Исполнитель с id = @{executor_id} '
                                                              f'успешно добавлен', reply_markup=kb)

    async def show_all_executors(self,message: Message):
        """ Хендлер для команды 'Показать исполнителей' """
        executors = await self.executor_db.select_all_executors()

        if executors == []:
            kb = self.executor_kb.add(GENERAL_BUTTONS)
            await self.bot.send_message(message.from_user.id, f"В системе еще не добавлен ни один исполнитель",
                                        reply_markup=kb)
            return

        existing_executors_id = []  # type: List[str]

        for executor in executors:
            for executor_id in executor:
                existing_executors_id.append(executor_id)

        for existing_executor_id in existing_executors_id:
            await self.bot.send_message(message.from_user.id, f'id исполнителя: @{existing_executor_id}',
                                        reply_markup=ReplyKeyboardRemove())

        kb = self.executor_kb.add(GENERAL_BUTTONS)
        await self.bot.send_message(message.from_user.id, f'Главное меню', reply_markup=kb)

    async def delete_executor(self, message: Message):
        """ Хендлер для команды 'Удалить исполнителя' """
        # ограничение на использование хендлера (могут использовать только админы)
        if message.from_user.username.lower() not in ADMINS:
            kb = self.executor_kb.add(GENERAL_BUTTONS)
            await self.bot.send_message(message.from_user.id, f'Вы не имеете доступ к удалению исполнителя',
                                        reply_markup=kb)
            return

        await self.fsm_executor.delete_executor.set()
        kb = self.executor_kb.add([EXECUTOR_BUTTONS.get("executor")[-1]])
        await message.reply("Введите id исполнителя, которого хотели бы удалить", reply_markup=kb)

    async def cancel(self, message: Message, state: FSMContext):
        """ Выход из машины состояний """
        current_state = await state.get_state()
        if current_state is not None:
            await state.finish()
        kb = self.executor_kb.add(GENERAL_BUTTONS)
        await self.bot.send_message(message.from_user.id, 'Главное меню', reply_markup=kb)

    async def input_delete_executor(self, message: Message, state: FSMContext):
        """ Хендлер для ввода id исполнителя, которого необходимо удалить """

        executor_id = message.text.lower()
        existing_executor = await self.executor_db.select_executor_id(executor_id=executor_id)

        if existing_executor is None:
            kb = self.executor_kb.add([EXECUTOR_BUTTONS.get("executor")[-1]])
            await message.reply(f'Исполнителя с id = {executor_id} не существует\n'
                                'Повторите попытку', reply_markup=kb)
        else:
            task_db = TaskDb()
            db_tasks = await task_db.select_task_by_executor_id(executor_id=executor_id)

            tasks = []  # type: List[Task]

            for db_task in db_tasks:
                task = Task()
                task.from_tuple(db_task)
                tasks.append(task)

            for task in tasks:
                # если существует выполняющаяся задача с удаляемым исполнителем, то исполнитель убирается,
                # а статус переходит в "не выполняется"
                if task.executor_id == executor_id and task.status == TASK_STATUS[1]:
                    task.executor_id = "Не назначен"
                    task.status = TASK_STATUS[0]

            for task in tasks:
                db_data_task = task.to_dict()
                await task_db.update_task_by_uuid(data=db_data_task, uuid=task.uuid)

            await self.executor_db.delete_executor(executor_id=executor_id)
            await state.finish()
            kb = self.executor_kb.add(GENERAL_BUTTONS)
            await self.bot.send_message(message.from_user.id, f'Исполнитель с id = {executor_id} успешно удален',
                                        reply_markup=kb)

    def registration(self, dp: Dispatcher):
        """Регистрация хендлеров для исполнителей"""
        dp.register_message_handler(callback=self.executors, commands=['Исполнители'])
        dp.register_message_handler(callback=self.add_executor, commands=['Добавить_исполнителя'],
                                    state=None)
        dp.register_message_handler(callback=self.show_all_executors, commands=['Показать_исполнителей'],
                                    state=None)
        dp.register_message_handler(callback=self.delete_executor, commands=['Удалить_исполнителя'],
                                    state=None)
        dp.register_message_handler(callback=self.cancel, commands=['Отмена'],
                                    state=None)

        # Добавление исполнителя
        dp.register_message_handler(callback=self.load_executor_id,
                                    state=self.fsm_executor.executor_id)
        # Удаление исполнителя
        dp.register_message_handler(callback=self.input_delete_executor,
                                    state=self.fsm_executor.delete_executor)
