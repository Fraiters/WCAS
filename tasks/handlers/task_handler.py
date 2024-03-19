from typing import List, Tuple
from aiogram import Bot, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.types import Message
from aiogram.types import ReplyKeyboardRemove
from settings import TASK_BUTTONS, GENERAL_BUTTONS
from models.task import Task, TASK_STATUS
from tasks.db.task_db import TaskBaseDb
from tasks.keyboards.task_kb import TaskKb
from utils.utils import is_datetime


class FsmTask(StatesGroup):
    """ Класс машины состояний для задач """
    title = State()
    description = State()
    priority = State()
    deadline = State()
    executor_type = State()
    prepare_executor_id = State()
    executor_id = State()
    check_task = State()

    show_by_executor_id = State()
    show_by_uuid = State()

    delete_task = State()


class TaskHandler:
    """ Класс хендлеров для задач """

    def __init__(self, bot: Bot, db_name: str):
        self.bot = bot
        self.task_kb = TaskKb()
        self.fsm_task = FsmTask()
        self.task_db = TaskBaseDb(db_name=db_name)
        self.task = ...  # type: Task

    # Уровень клавиатуры 1
    # /Добавить задачу, /Показать задачу
    async def tasks(self, message: Message):
        """ Хендлер для команды 'Задачи' """
        kb = self.task_kb.add(TASK_BUTTONS.get("task"))
        await self.bot.send_message(message.from_user.id, 'Чтобы добавить задачу нажмите на "/Добавить_задачу" \n'
                                                          'Чтобы посмотреть отчеты нажмите на "Показать"'
                                                          'для отмены введите команду "/Отмена"', reply_markup=kb)

    # Уровень клавиатуры 2
    # Добавить задачу:
    async def add_task(self, message: Message):
        """ Хендлер для команды 'Добавить задачу' (Вход в машину состояний) """
        await self.fsm_task.title.set()
        await message.reply("Введите заголовок задачи", reply_markup=ReplyKeyboardRemove())

    # Уровень клавиатуры 2
    # Показать задачи:
    # /Показать_все_задачи, /Показать_задачи_по_id_исполнителя, /Показать_задачу_по_уникальному_id
    async def show_task(self, message: Message):
        """ Хендлер для команды 'Показать задачу' """
        kb = self.task_kb.add(TASK_BUTTONS.get("show_tasks"))
        await message.reply("Выберите параметры просмотра", reply_markup=kb)

    # Уровень клавиатуры 2
    # Удалить задачу:
    async def input_delete_task(self, message: Message):
        """ Хендлер для ввода id для удаления задачи """
        await self.fsm_task.delete_task.set()
        await message.reply("Введите id задачи, которую хотели бы удалить", reply_markup=ReplyKeyboardRemove())

    async def cancel(self, message: Message, state: FSMContext):
        """ Выход из машины состояний """
        current_state = await state.get_state()
        if current_state is None:
            return
        await state.finish()
        kb = self.task_kb.add(GENERAL_BUTTONS)
        await self.bot.send_message(message.from_user.id, 'Главное меню', reply_markup=kb)

    async def delete_task(self, message: Message, state: FSMContext):
        """ Хендлер для команды 'Удалить задачу' """
        try:
            uuid = int(message.text)
            db_task = await self.task_db.select_task_by_uuid(uuid=uuid)
            if db_task is None:
                await message.reply(f'Задачи с id = {uuid} не существует\n'
                                    'Повторите попытку')
            else:
                await self.task_db.delete_task(uuid=uuid)
                await state.finish()
                kb = self.task_kb.add(GENERAL_BUTTONS)
                await self.bot.send_message(message.from_user.id, f'Задача с id = {uuid} успешно удалена',
                                            reply_markup=kb)

        except ValueError:
            await message.reply('Неверный формат записи id\n'
                                'Повторите попытку')

    async def show_all_tasks(self, message: Message):
        """ Хендлер для команды 'Показать все задачи' """
        db_tasks = await self.task_db.select_all_tasks()  # type: List[Tuple]

        tasks = []  # type: List[Task]

        for uuid, title in db_tasks:
            task = Task(message=message)
            task.uuid = uuid
            task.title = title
            tasks.append(task)

        for task in tasks:
            await message.answer(f"id задачи: {task.uuid}\n"
                                 f"Название задачи: {task.title}\n", reply_markup=ReplyKeyboardRemove())

        kb = self.task_kb.add(GENERAL_BUTTONS)
        await self.bot.send_message(message.from_user.id, 'Главное меню', reply_markup=kb)

    async def input_executor_id(self, message: Message):
        """Хендлер для ввода executor_id для команды 'Показать задачи по id исполнителя' """

        await self.fsm_task.show_by_executor_id.set()
        await self.bot.send_message(message.from_user.id, "Введите id исполнителя (через @)",
                                    reply_markup=ReplyKeyboardRemove())

    async def show_task_by_executor_id(self, message: Message, state: FSMContext):
        """ Хендлер для команды 'Показать задачу по id исполнителя' """
        executor_id = message.text
        db_tasks = await self.task_db.select_task_by_executor_id(executor_id=executor_id)
        tasks = []  # type: List[Task]

        if db_tasks == []:
            await message.reply(f'Задачи с id исполнителя = {executor_id} не найдены\n'
                                'Повторите попытку', reply_markup=ReplyKeyboardRemove())
        else:
            for uuid, title, description, status, priority, deadline, executor_type, executor_id in db_tasks:
                task = Task(message=message)
                task.uuid = uuid
                task.title = title
                task.description = description
                task.status = status
                task.priority = priority
                task.deadline = deadline
                task.executor_type = executor_type
                task.executor_id = executor_id
                tasks.append(task)

            await state.finish()

            for task in tasks:
                await message.answer(f"id задачи: {task.uuid}\n"
                                     f"Название задачи: {task.title}\n"
                                     f"Содержание: \n{task.description}\n\n"
                                     f"Готовность: {task.status}\n"
                                     f"Приоритет: {task.priority}\n"
                                     f"Срок выполнения: {task.deadline}\n"
                                     f"Тип исполнителя: {task.executor_type}\n"
                                     f"Исполнитель: {task.executor_id}\n", reply_markup=ReplyKeyboardRemove())

            kb = self.task_kb.add(GENERAL_BUTTONS)
            await self.bot.send_message(message.from_user.id, 'Главное меню', reply_markup=kb)

    async def input_uuid(self, message: Message):
        """Хендлер для ввода uuid для команды 'Показать задачу по уникальному id' """

        await self.fsm_task.show_by_uuid.set()
        await self.bot.send_message(message.from_user.id, "Введите уникальный id задачи",
                                    reply_markup=ReplyKeyboardRemove())

    async def show_task_by_uuid(self, message: Message, state: FSMContext):
        """ Хендлер для команды 'Показать задачу по уникальному id' """
        try:
            uuid = int(message.text)
            db_task = await self.task_db.select_task_by_uuid(uuid=uuid)
            if db_task is None:
                await message.reply(f'Отчета с id = {uuid} не существует\n'
                                    'Повторите попытку')
            else:
                task = Task(message=message)
                for uuid, title, description, status, priority, deadline, executor_type, executor_id in [db_task]:
                    task.uuid = uuid
                    task.title = title
                    task.description = description
                    task.status = status
                    task.priority = priority
                    task.deadline = deadline
                    task.executor_type = executor_type
                    task.executor_id = executor_id

                await state.finish()
                await message.answer(f"id задачи: {task.uuid}\n"
                                     f"Название задачи: {task.title}\n"
                                     f"Содержание: \n{task.description}\n\n"
                                     f"Готовность: {task.status}\n"
                                     f"Приоритет: {task.priority}\n"
                                     f"Срок выполнения: {task.deadline}\n"
                                     f"Тип исполнителя: {task.executor_type}\n"
                                     f"Исполнитель: {task.executor_id}\n", reply_markup=ReplyKeyboardRemove())

                kb = self.task_kb.add(GENERAL_BUTTONS)
                await self.bot.send_message(message.from_user.id, 'Главное меню', reply_markup=kb)

        except ValueError:
            await message.reply('Неверный формат записи id\n'
                                'Повторите попытку')

    async def load_title(self, message: Message, state: FSMContext):
        """Загрузка заголовка задачи"""
        async with state.proxy() as data:
            data['title'] = message.text
            # TO DO: добавить отловку исключения на создание не уникального title
        await self.fsm_task.next()
        await message.reply('Введите описание задачи', reply_markup=ReplyKeyboardRemove())

    async def load_description(self, message: Message, state: FSMContext):
        """Загрузка описания"""
        async with state.proxy() as data:
            data['description'] = message.text
        await self.fsm_task.next()
        kb = self.task_kb.add(TASK_BUTTONS.get("priority"))
        await message.reply('Выберите приоритет задачи', reply_markup=kb)

    async def load_priority(self, message: Message, state: FSMContext):
        """Загрузка приоритета"""
        async with state.proxy() as data:
            data['priority'] = message.text[1:]
        await self.fsm_task.next()
        await message.reply('Введите дедлайн для выполнения задачи dd.mm.yyyy', reply_markup=ReplyKeyboardRemove())

    async def load_deadline(self, message: Message, state: FSMContext):
        """Загрузка дедлайна"""
        if is_datetime(date=message.text):
            async with state.proxy() as data:
                data['deadline'] = message.text
            await self.fsm_task.next()
            kb = self.task_kb.add(TASK_BUTTONS.get("executor_type"))
            await message.reply('Выберите тип исполнителя', reply_markup=kb)

        else:
            await message.reply('Неверный формат записи даты\n'
                                'Повторите попытку (правильный формат: dd.mm.yyyy)')

    async def load_executor_type(self, message: Message, state: FSMContext):
        """Загрузка типа исполнителя"""
        async with state.proxy() as data:
            data['executor_type'] = message.text[1:]
        await self.fsm_task.next()
        kb = self.task_kb.add(TASK_BUTTONS.get("prepare_executor_id"))
        await message.reply('Желаете сразу назначить исполнителя задачи?', reply_markup=kb)

    async def prepare_executor_id(self, message: Message, state: FSMContext):
        """Подготовка к вводу id исполнителя"""
        if message.text == TASK_BUTTONS.get("prepare_executor_id")[1]:
            async with state.proxy() as data:
                data['status'] = TASK_STATUS[0]
                self.task = Task(message=message)
                self.task.from_dict(data=data)
                await self.task.print_info()

            await self.fsm_task.check_task.set()
            kb = self.task_kb.add(TASK_BUTTONS.get("check_task"))
            await self.bot.send_message(message.from_user.id, "Все верно?", reply_markup=kb)

        elif message.text == TASK_BUTTONS.get("prepare_executor_id")[0]:
            await self.fsm_task.next()
            await message.reply('Введите id исполнителя задачи через @', reply_markup=ReplyKeyboardRemove())

    async def load_executor_id(self, message: Message, state: FSMContext):
        """Загрузка id исполнителя"""
        async with state.proxy() as data:
            data['executor_id'] = message.text

        async with state.proxy() as data:
            data['status'] = TASK_STATUS[1]
            self.task = Task(message=message)
            self.task.from_dict(data=data)
            await self.task.print_info()

        await self.fsm_task.check_task.set()
        kb = self.task_kb.add(TASK_BUTTONS.get("check_task"))
        await self.bot.send_message(message.from_user.id, "Все верно?", reply_markup=kb)

    async def check_task(self, message: Message, state: FSMContext):
        """Проверка задачи"""
        if message.text == TASK_BUTTONS.get("check_task")[1]:
            await state.reset_data()
            await self.fsm_task.title.set()
            await message.reply("Введите заголовок задачи:", reply_markup=ReplyKeyboardRemove())

        elif message.text == TASK_BUTTONS.get("check_task")[0]:
            db_data = self.task.to_dict()
            await self.task_db.insert_record_task(data=db_data)
            uuid = await self.task_db.select_uuid_by_title(title=self.task.title)
            await self.task.set_uuid(uuid=uuid)

            await self.bot.send_message(message.from_user.id, "Задача создана и сохранена\n"
                                                              f"id задачи: {self.task.uuid}",
                                        reply_markup=ReplyKeyboardRemove())
            await state.finish()
            kb = self.task_kb.add(GENERAL_BUTTONS)
            await self.bot.send_message(message.from_user.id, 'Главное меню', reply_markup=kb)
        else:
            kb = self.task_kb.add(TASK_BUTTONS.get("check_task"))
            await message.reply('Такой команды нет\n'
                                'Повторите попытку', reply_markup=kb)

    def registration(self, dp: Dispatcher):
        """Регистрация хендлеров для задач"""
        dp.register_message_handler(callback=self.tasks, commands=['Задачи'])
        dp.register_message_handler(callback=self.add_task, commands=['Добавить_задачу'],
                                    state=None)
        dp.register_message_handler(callback=self.show_task, commands=['Показать_задачу'],
                                    state=None)
        dp.register_message_handler(callback=self.input_delete_task, commands=['Удалить_задачу'],
                                    state=None)
        dp.register_message_handler(callback=self.cancel, commands=['Отмена'],
                                    state='*')
        dp.register_message_handler(self.cancel, Text(equals='Отмена', ignore_case=True),
                                    state='*')

        # Добавление задачи
        dp.register_message_handler(callback=self.load_title,
                                    state=self.fsm_task.title)
        dp.register_message_handler(callback=self.load_description,
                                    state=self.fsm_task.description)
        dp.register_message_handler(callback=self.load_priority,
                                    state=self.fsm_task.priority)
        dp.register_message_handler(callback=self.load_deadline,
                                    state=self.fsm_task.deadline)
        dp.register_message_handler(callback=self.load_executor_type,
                                    state=self.fsm_task.executor_type)
        dp.register_message_handler(callback=self.prepare_executor_id,
                                    state=self.fsm_task.prepare_executor_id)
        dp.register_message_handler(callback=self.load_executor_id,
                                    state=self.fsm_task.executor_id)
        dp.register_message_handler(callback=self.check_task,
                                    state=self.fsm_task.check_task)
        # Просмотр задачи
        dp.register_message_handler(callback=self.show_all_tasks, commands=['Показать_все_задачи'],
                                    state=None)
        dp.register_message_handler(callback=self.input_executor_id, commands=['Показать_задачи_по_id_исполнителя'],
                                    state=None)
        dp.register_message_handler(callback=self.input_uuid, commands=['Показать_задачу_по_уникальному_id'],
                                    state=None)
        dp.register_message_handler(callback=self.show_task_by_executor_id,
                                    state=self.fsm_task.show_by_executor_id)
        dp.register_message_handler(callback=self.show_task_by_uuid,
                                    state=self.fsm_task.show_by_uuid)

        # Удаление задачи
        dp.register_message_handler(callback=self.delete_task,
                                    state=self.fsm_task.delete_task)
