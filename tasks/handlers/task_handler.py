from typing import List, Tuple, Union
from aiogram import Bot, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.types import Message
from aiogram.types import ReplyKeyboardRemove

from executor_rating.db.executor_rating_db import ExecutorRatingDb
from executor_rating.executor_rating import ExecutorRating
from performance_indicator.general_performance_indicator import GeneralPerformanceIndicator
from performance_indicator.performance_indicator import PerformanceIndicator
from settings import TASK_BUTTONS, GENERAL_BUTTONS
from models.task import Task, TASK_STATUS
from tasks.db.task_db import TaskDb
from tasks.keyboards.task_kb import TaskKb
from user.db.user_db import UserDb
from user.user_settings import EXECUTORS, ANALYTICS, ADMINS
from utils.utils import is_datetime, set_available_users


class FsmTask(StatesGroup):
    """ Класс машины состояний для задач """
    title = State()
    description = State()
    complexity = State()
    deadline = State()
    prepare_previous_task = State()
    previous_task = State()
    check_previous_task = State()
    prepare_next_task = State()
    check_next_task = State()
    next_task = State()
    executor_type = State()
    prepare_executor_id = State()
    executor_id = State()
    check_add_task = State()

    upd_uuid = State()
    check_upd_task = State()

    show_by_executor_id = State()
    show_by_uuid = State()

    delete_task = State()

    assign_task = State()
    assign_executor_id = State()

    closing_task = State()


class TaskHandler:
    """ Класс хендлеров для задач """

    def __init__(self, bot: Bot):
        self.bot = bot
        self.task_kb = TaskKb()
        self.fsm_task = FsmTask()
        self.task_db = TaskDb()
        self.task = ...  # type: Task

    # Уровень клавиатуры 1
    # /Добавить задачу, /Показать задачу, /Редактировать задачу, /Удалить задачу
    async def tasks(self, message: Message):
        """ Хендлер для команды 'Задачи' """
        kb = self.task_kb.add(TASK_BUTTONS.get("task"))
        await self.bot.send_message(message.from_user.id, 'Чтобы добавить задачу нажмите на "/Добавить_задачу"\n\n'
                                                          'Чтобы посмотреть отчеты нажмите на "/Показать"\n\n'
                                                          'Чтобы обновить задачу нажмите на "/Редактировать_задачу"\n\n'
                                                          'Чтобы удалить задачу нажмите на "/Удалить_задачу"\n\n'
                                                          'Чтобы назначить задачу на исполнителя нажмите на'
                                                          '"/Назначить_задачу"\n\n'
                                                          'Чтобы закрыть задачу нажмите на /Закрыть_задачу\n\n'
                                                          'Для отмены введите команду "/Отмена"', reply_markup=kb)

    # Уровень клавиатуры 2
    # Добавить задачу:
    async def add_task(self, message: Message):
        """ Хендлер для команды 'Добавить задачу' (Вход в машину состояний) """
        # ограничение на использование хендлера (могут использовать аналитики и админы)
        users = list(set(ANALYTICS + ADMINS))

        available_users = list(map(int, await set_available_users(users=users)))  # type: List[int]

        if message.from_user.id not in available_users:
            kb = self.task_kb.add(GENERAL_BUTTONS)
            await self.bot.send_message(message.from_user.id, f'Вы не имеете доступ к созданию задачи',
                                        reply_markup=kb)
            return

        self.task = Task()
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
    # Редактировать задачу:
    async def upd_task(self, message: Message):
        """ Хендлер для команды 'Редактировать задачу' (Вход в машину состояний) """
        # ограничение на использование хендлера (могут использовать аналитики и админы)
        users = list(set(ANALYTICS + ADMINS))

        available_users = list(map(int, await set_available_users(users=users)))  # type: List[int]

        if message.from_user.id not in available_users:
            kb = self.task_kb.add(GENERAL_BUTTONS)
            await self.bot.send_message(message.from_user.id, f'Вы не имеете доступ к обновлению задачи',
                                        reply_markup=kb)
            return

        self.task = Task()
        await self.fsm_task.upd_uuid.set()
        await message.reply("Введите id задачи, которую хотели бы изменить", reply_markup=ReplyKeyboardRemove())

    # Уровень клавиатуры 2
    # Удалить задачу:
    async def input_delete_task(self, message: Message):
        """ Хендлер для ввода id для удаления задачи """
        # ограничение на использование хендлера (могут использовать аналитики и админы)
        users = list(set(ANALYTICS + ADMINS))

        available_users = list(map(int, await set_available_users(users=users)))  # type: List[int]

        if message.from_user.id not in available_users:
            kb = self.task_kb.add(GENERAL_BUTTONS)
            await self.bot.send_message(message.from_user.id, f'Вы не имеете доступ к удалению задачи',
                                        reply_markup=kb)
            return
        await self.fsm_task.delete_task.set()
        await message.reply("Введите id задачи, которую хотели бы удалить", reply_markup=ReplyKeyboardRemove())

    # Уровень клавиатуры 2
    # Назначить задачу:
    async def input_assign_task(self, message: Message):
        """ Хендлер для ввода id для назначения задачи """
        await self.fsm_task.assign_task.set()
        await message.reply("Введите id задачи, которую хотели бы назначить на исполнителя",
                            reply_markup=ReplyKeyboardRemove())

    # Уровень клавиатуры 2
    # /Назначить_задачу
    async def input_closing_task(self, message: Message):
        """ Хендлер для ввода id для закрытия задачи """
        # ограничение на использование хендлера (могут использовать исполнители и админы)
        users = list(set(EXECUTORS + ADMINS))

        available_users = list(map(int, await set_available_users(users=users)))  # type: List[int]

        if message.from_user.id not in available_users:
            kb = self.task_kb.add(GENERAL_BUTTONS)
            await self.bot.send_message(message.from_user.id, f'Вы не имеете доступ к закрытию задачи',
                                        reply_markup=kb)
            return

        await self.fsm_task.closing_task.set()
        await message.reply("Введите id задачи, которую хотите закрыть", reply_markup=ReplyKeyboardRemove())

    async def cancel(self, message: Message, state: FSMContext):
        """ Выход из машины состояний """
        current_state = await state.get_state()
        if current_state is None:
            return
        await state.finish()
        kb = self.task_kb.add(GENERAL_BUTTONS)
        await self.bot.send_message(message.from_user.id, 'Главное меню', reply_markup=kb)

    async def load_upd_uuid(self, message: Message):
        """ Загрузка id задачи, которую необходимо изменить """
        try:
            uuid = int(message.text)
            db_task = await self.task_db.select_task_by_uuid(uuid=uuid)
            if db_task is None:
                await message.reply(f'Задачи с id = {uuid} не существует\n'
                                    'Повторите попытку')
            else:
                await self.task.set_uuid(uuid=uuid)
                await self.fsm_task.title.set()
                await message.reply("Введите заголовок задачи", reply_markup=ReplyKeyboardRemove())
        except ValueError:
            await message.reply('Неверный формат записи id\n'
                                'Повторите попытку')

    async def check_upd_task(self, message: Message, state: FSMContext):
        """ Проверка измененной задачи """
        if message.text == TASK_BUTTONS.get("check_task")[1]:
            await state.reset_data()
            await self.fsm_task.title.set()
            await message.reply("Введите заголовок задачи:", reply_markup=ReplyKeyboardRemove())

        elif message.text == TASK_BUTTONS.get("check_task")[0]:
            db_data = self.task.to_dict()
            uuid = self.task.uuid

            await self.task_db.update_task_by_uuid(data=db_data, uuid=uuid)

            # Обновление данных у предыдущей связанной задачи
            if self.task.previous_task != "Нет":
                db_previous_task = await self.task_db.select_task_by_uuid(uuid=int(self.task.previous_task))
                if db_previous_task is not None:
                    old_task = Task()
                    old_task.from_tuple(data=db_previous_task)
                    old_task.next_task = self.task.uuid
                    db_old_task = old_task.to_dict()
                    await self.task_db.update_task_by_uuid(data=db_old_task, uuid=old_task.uuid)
            # Обновление данных у следующей связанной задачи
            if self.task.next_task != "Нет":
                db_next_task = await self.task_db.select_task_by_uuid(uuid=int(self.task.next_task))
                if db_next_task is not None:
                    old_task = Task()
                    old_task.from_tuple(data=db_next_task)
                    old_task.previous_task = self.task.uuid
                    db_old_task = old_task.to_dict()
                    await self.task_db.update_task_by_uuid(data=db_old_task, uuid=old_task.uuid)

            await self.bot.send_message(message.from_user.id, "Задача изменена и сохранена\n"
                                                              f"id задачи: {self.task.uuid}",
                                        reply_markup=ReplyKeyboardRemove())

            await state.finish()

            # Оповещение пользователя о его назначении на задачу
            if self.task.executor_id != "Не назначен":
                user_db = UserDb()
                user_id = await user_db.select_user_id_by_username(username=self.task.executor_id)
                await self.bot.send_message(user_id,
                                            f"Вас назначили на задачу {self.task.title} с id = {self.task.uuid}",
                                            reply_markup=ReplyKeyboardRemove())

            kb = self.task_kb.add(GENERAL_BUTTONS)
            await self.bot.send_message(message.from_user.id, 'Главное меню', reply_markup=kb)
        else:
            kb = self.task_kb.add(TASK_BUTTONS.get("check_task"))
            await message.reply('Такой команды нет\n'
                                'Повторите попытку', reply_markup=kb)

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

    async def assign_task(self, message: Message):
        """ Хендлер для команды 'Назначить задачу' """
        try:
            uuid = int(message.text)
            db_task = await self.task_db.select_task_by_uuid(uuid=uuid)
            if db_task is None:
                await message.reply(f'Задачи с id = {uuid} не существует\n'
                                    'Повторите попытку')
            else:
                self.task = Task()
                self.task.from_tuple(data=db_task)

                # Проверка статуса задачи
                if self.task.status == TASK_STATUS[2]:
                    await message.reply(f'Задача с id = {uuid} уже выполнена\n'
                                        'Повторите попытку')
                    await self.fsm_task.assign_task.set()

                elif self.task.status == TASK_STATUS[1]:
                    kb = self.task_kb.add([TASK_BUTTONS.get("task")[-1]])
                    await self.fsm_task.assign_executor_id.set()

                    await message.reply(f'Задача с id = {uuid} уже выполняется и назначена на исполнителя.\n'
                                        'Если вы желаете переназначить исполнителя, то введите его id (без знака @)\n'
                                        'Если хотите выйти из меню назначения, то введите команду /Отмена',
                                        reply_markup=kb)

                elif self.task.status == TASK_STATUS[0]:

                    await self.fsm_task.assign_executor_id.set()
                    await self.bot.send_message(message.from_user.id, "Введите id исполнителя (без знака @)",
                                                reply_markup=ReplyKeyboardRemove())

        except ValueError:
            await message.reply('Неверный формат записи id\n'
                                'Повторите попытку')

    async def assign_executor_id(self, message: Message, state: FSMContext):
        """ Хендлер для назначения executor_id на задачу """
        executor_id = message.text.lower()

        if executor_id not in EXECUTORS:
            await message.reply(f'Исполнителя с id = {executor_id} не существует\n'
                                'Повторите попытку')
            await self.fsm_task.assign_executor_id.set()
        else:
            self.task.executor_id = executor_id
            self.task.status = TASK_STATUS[1]
            db_data = self.task.to_dict()
            uuid = self.task.uuid

            await self.task_db.update_task_by_uuid(data=db_data, uuid=uuid)

            await state.finish()
            await message.reply(f'Исполнителя @{executor_id} назначили на задачу с id = {self.task.uuid}\n')
            # Оповещение пользователя о его назначении на задачу
            user_db = UserDb()
            user_id = await user_db.select_user_id_by_username(username=executor_id)
            await self.bot.send_message(user_id,
                                        f"Вас назначили на задачу {self.task.title} с id = {self.task.uuid}",
                                        reply_markup=ReplyKeyboardRemove())

            kb = self.task_kb.add(GENERAL_BUTTONS)
            await self.bot.send_message(message.from_user.id, 'Главное меню', reply_markup=kb)

    async def show_all_tasks(self, message: Message):
        """ Хендлер для команды 'Показать все задачи' """
        db_tasks = await self.task_db.select_all_tasks()  # type: List[Tuple]

        tasks = []  # type: List[Task]
        for uuid, title in db_tasks:
            task = Task()
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
        await self.bot.send_message(message.from_user.id, "Введите id исполнителя (без знака @)",
                                    reply_markup=ReplyKeyboardRemove())

    async def show_task_by_executor_id(self, message: Message, state: FSMContext):
        """ Хендлер для команды 'Показать задачу по id исполнителя' """
        executor_id = message.text.lower()
        db_tasks = await self.task_db.select_task_by_executor_id(executor_id=executor_id)
        tasks = []  # type: List[Task]

        if db_tasks == []:
            await message.reply(f'Задачи с id исполнителя = {executor_id} не найдены\n'
                                'Повторите попытку', reply_markup=ReplyKeyboardRemove())
        else:
            for uuid, title, description, status, complexity, deadline, closing_date, previous_task, next_task, \
                    executor_type, executor_id in db_tasks:
                task = Task()
                task.uuid = uuid
                task.title = title
                task.description = description
                task.status = status
                task.complexity = complexity
                task.deadline = deadline
                task.closing_date = closing_date
                task.previous_task = previous_task
                task.next_task = next_task
                task.executor_type = executor_type
                task.executor_id = executor_id
                tasks.append(task)

            await state.finish()
            for task in tasks:
                await message.answer(f"id задачи: {task.uuid}\n"
                                     f"Название задачи: {task.title}\n"
                                     f"Содержание: \n{task.description}\n\n"
                                     f"Готовность: {task.status}\n"
                                     f"Сложность: {task.complexity}\n"
                                     f"Срок выполнения: {task.deadline}\n"
                                     f"Тип исполнителя: {task.executor_type}\n"
                                     f"Исполнитель: @{task.executor_id}\n\n",
                                     f"Предыдущая связанная задача (id): {task.previous_task}\n"
                                     f"Следующая связанная задача (id): {task.next_task}\n"
                                     f"Дата закрытия задачи: {task.closing_date}\n",
                                     reply_markup=ReplyKeyboardRemove())

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
                await message.reply(f'Задачи с id = {uuid} не существует\n'
                                    'Повторите попытку')
            else:
                task = Task()
                task.from_tuple(data=db_task)

                await state.finish()
                await message.answer(f"id задачи: {task.uuid}\n"
                                     f"Название задачи: {task.title}\n"
                                     f"Содержание: \n{task.description}\n\n"
                                     f"Готовность: {task.status}\n"
                                     f"Сложность: {task.complexity}\n"
                                     f"Срок выполнения: {task.deadline}\n"
                                     f"Тип исполнителя: {task.executor_type}\n"
                                     f"Исполнитель: @{task.executor_id}\n\n"
                                     f"Предыдущая связанная задача (id): {task.previous_task}\n"
                                     f"Следующая связанная задача (id): {task.next_task}\n"
                                     f"Дата закрытия задачи: {task.closing_date}\n",
                                     reply_markup=ReplyKeyboardRemove())

                kb = self.task_kb.add(GENERAL_BUTTONS)
                await self.bot.send_message(message.from_user.id, 'Главное меню', reply_markup=kb)

        except ValueError:
            await message.reply('Неверный формат записи id\n'
                                'Повторите попытку')

    async def load_title(self, message: Message, state: FSMContext):
        """ Загрузка заголовка задачи """
        async with state.proxy() as data:
            data['title'] = message.text
            # Исключение на создание задачи с не уникальным title
            task_id = await self.task_db.select_uuid_by_title(title=data['title'])
            if task_id is not None:
                await message.reply(f'Задача с таким названием уже существует \n'
                                    'Повторите попытку')
                await self.fsm_task.title.set()
                await message.reply("Введите название задачи", reply_markup=ReplyKeyboardRemove())
                return
        await self.fsm_task.description.set()
        await message.reply('Введите описание задачи', reply_markup=ReplyKeyboardRemove())

    async def load_description(self, message: Message, state: FSMContext):
        """ Загрузка описания """
        async with state.proxy() as data:
            data['description'] = message.text
        await self.fsm_task.complexity.set()
        kb = self.task_kb.add(TASK_BUTTONS.get("complexity"))
        await message.reply('Выберите сложность задачи', reply_markup=kb)

    async def load_complexity(self, message: Message, state: FSMContext):
        """Загрузка сложности"""
        async with state.proxy() as data:
            data['complexity'] = message.text[1:]
        await self.fsm_task.deadline.set()
        await message.reply('Введите дедлайн для выполнения задачи dd.mm.yyyy', reply_markup=ReplyKeyboardRemove())

    async def load_deadline(self, message: Message, state: FSMContext):
        """ Загрузка дедлайна """
        if is_datetime(date=message.text):
            async with state.proxy() as data:
                data['deadline'] = message.text
            await self.fsm_task.prepare_previous_task.set()
            kb = self.task_kb.add(TASK_BUTTONS.get("prepare"))
            await message.reply('Желаете назначить предыдущую связанную задачу?', reply_markup=kb)

        else:
            await message.reply('Неверный формат записи даты\n'
                                'Повторите попытку (правильный формат: dd.mm.yyyy)')

    async def prepare_previous_task(self, message: Message):
        """ Подготовка к вводу предыдущей связанной задачи """
        if message.text == TASK_BUTTONS.get("prepare")[1]:
            await self.fsm_task.prepare_next_task.set()
            kb = self.task_kb.add(TASK_BUTTONS.get("prepare"))
            await message.reply('Желаете назначить следующую связанную задачу?', reply_markup=kb)

        elif message.text == TASK_BUTTONS.get("prepare")[0]:
            await self.fsm_task.previous_task.set()
            await message.reply('Введите id связанной предыдущей задачи', reply_markup=ReplyKeyboardRemove())

    async def load_previous_task(self, message: Message, state: FSMContext):
        """ Загрузка предыдущей задачи """
        try:
            uuid = int(message.text)
            db_task = await self.task_db.select_task_by_uuid(uuid=uuid)  # type: Tuple

            if db_task is None:
                await message.reply(f'Задачи с id = {uuid} не существует\n'
                                    'Повторите попытку')
                await self.fsm_task.previous_task.set()
                return
            else:
                task = Task()
                task.from_tuple(data=db_task)
                # если следующая задача у связанной предыдущей задачи не назначена
                if task.next_task == "Нет" or task.next_task is None:
                    async with state.proxy() as data:
                        data['previous_task'] = uuid

                    await self.fsm_task.prepare_next_task.set()
                    kb = self.task_kb.add(TASK_BUTTONS.get("prepare"))
                    await message.reply('Желаете назначить следующую связанную задачу?', reply_markup=kb)
                # если следующая задача у связанной предыдущей задачи уже назначена
                else:
                    async with state.proxy() as data:
                        data['previous_task'] = uuid

                    await self.fsm_task.check_previous_task.set()
                    kb = self.task_kb.add(TASK_BUTTONS.get("check_task"))
                    await message.reply('!ВНИМАНИЕ!\n'
                                        'У выбранной предыдущей связанной задачи уже есть связанная следующая задача\n'
                                        'Желаете продолжить?', reply_markup=kb)

        except ValueError:
            await message.reply('Неверный формат записи id\n'
                                'Повторите попытку')

    async def check_previous_task(self, message: Message, state: FSMContext):
        """ Проверка предыдущей связанной задачи"""
        if message.text == TASK_BUTTONS.get("check_task")[1]:
            # обнуляем значение предыдущей задачи
            async with state.proxy() as data:
                data['previous_task'] = None
            await self.fsm_task.previous_task.set()
            await message.reply('Введите заново id связанной предыдущей задачи', reply_markup=ReplyKeyboardRemove())

        elif message.text == TASK_BUTTONS.get("check_task")[0]:

            await self.fsm_task.prepare_next_task.set()
            kb = self.task_kb.add(TASK_BUTTONS.get("prepare"))
            await message.reply('Желаете назначить следующую связанную задачу?', reply_markup=kb)

    async def prepare_next_task(self, message: Message):
        """ Подготовка к вводу следующей связанной задачи """
        if message.text == TASK_BUTTONS.get("prepare")[1]:
            await self.fsm_task.executor_type.set()
            kb = self.task_kb.add(TASK_BUTTONS.get("executor_type"))
            await message.reply('Выберите тип исполнителя', reply_markup=kb)

        elif message.text == TASK_BUTTONS.get("prepare")[0]:
            await self.fsm_task.next_task.set()
            await message.reply('Введите id связанной следующей задачи', reply_markup=ReplyKeyboardRemove())

    async def load_next_task(self, message: Message, state: FSMContext):
        """ Загрузка следующей задачи """
        try:
            uuid = int(message.text)
            db_task = await self.task_db.select_task_by_uuid(uuid=uuid)  # type: Tuple

            if db_task is None:
                await message.reply(f'Задачи с id = {uuid} не существует\n'
                                    'Повторите попытку')
                await self.fsm_task.next_task.set()
                return
            else:
                task = Task()
                task.from_tuple(data=db_task)
                # если предыдущая задача у связанной следующей задачи не назначена
                if task.previous_task == "Нет" or task.previous_task is None:
                    async with state.proxy() as data:
                        data['next_task'] = uuid

                    await self.fsm_task.executor_type.set()
                    kb = self.task_kb.add(TASK_BUTTONS.get("executor_type"))
                    await message.reply('Выберите тип исполнителя', reply_markup=kb)
                # если предыдущая задача у связанной следующей задачи уже назначена
                else:
                    async with state.proxy() as data:
                        data['next_task'] = uuid

                    await self.fsm_task.check_next_task.set()
                    kb = self.task_kb.add(TASK_BUTTONS.get("check_task"))
                    await message.reply('!ВНИМАНИЕ!\n'
                                        'У выбранной следующей связанной задачи уже есть связанная предыдущая задача\n'
                                        'Желаете продолжить?', reply_markup=kb)

        except ValueError:
            await message.reply('Неверный формат записи id\n'
                                'Повторите попытку')

    async def check_next_task(self, message: Message, state: FSMContext):
        """ Проверка следующей связанной задачи"""
        if message.text == TASK_BUTTONS.get("check_task")[1]:
            # обнуляем значение следующей задачи
            async with state.proxy() as data:
                data['next_task'] = None
            await self.fsm_task.next_task.set()
            await message.reply('Введите заново id связанной следующей задачи', reply_markup=ReplyKeyboardRemove())

        elif message.text == TASK_BUTTONS.get("check_task")[0]:

            await self.fsm_task.executor_type.set()
            kb = self.task_kb.add(TASK_BUTTONS.get("executor_type"))
            await message.reply('Выберите тип исполнителя', reply_markup=kb)

    async def load_executor_type(self, message: Message, state: FSMContext):
        """ Загрузка типа исполнителя """
        async with state.proxy() as data:
            data['executor_type'] = message.text[1:]
        await self.fsm_task.prepare_executor_id.set()
        kb = self.task_kb.add(TASK_BUTTONS.get("prepare"))
        await message.reply('Желаете сразу назначить исполнителя задачи?', reply_markup=kb)

    async def prepare_executor_id(self, message: Message, state: FSMContext):
        """ Подготовка к вводу id исполнителя """
        if message.text == TASK_BUTTONS.get("prepare")[1]:
            async with state.proxy() as data:
                data['status'] = TASK_STATUS[0]
                self.task.from_dict(data=data)
                await self.task.print_info(message=message)

            if self.task.uuid is None:
                await self.fsm_task.check_add_task.set()
            else:
                await self.fsm_task.check_upd_task.set()

            kb = self.task_kb.add(TASK_BUTTONS.get("check_task"))
            await self.bot.send_message(message.from_user.id, "Все верно?", reply_markup=kb)

        elif message.text == TASK_BUTTONS.get("prepare")[0]:
            await self.fsm_task.executor_id.set()
            await message.reply('Введите id исполнителя задачи (без знака @)', reply_markup=ReplyKeyboardRemove())

    async def load_executor_id(self, message: Message, state: FSMContext):
        """ Загрузка id исполнителя """

        async with state.proxy() as data:
            executor_id = message.text.lower()

            if executor_id not in EXECUTORS:
                await message.reply(f'Исполнителя с id = {executor_id} не существует\n'
                                    'Повторите попытку')
                await self.fsm_task.executor_id.set()
                return

            data['executor_id'] = message.text.lower()
            data['status'] = TASK_STATUS[1]
            self.task.from_dict(data=data)
            await self.task.print_info(message=message)

        if self.task.uuid is None:
            await self.fsm_task.check_add_task.set()
        else:
            await self.fsm_task.check_upd_task.set()

        kb = self.task_kb.add(TASK_BUTTONS.get("check_task"))
        await self.bot.send_message(message.from_user.id, "Все верно?", reply_markup=kb)

    async def check_add_task(self, message: Message, state: FSMContext):
        """ Проверка добавленной задачи """
        if message.text == TASK_BUTTONS.get("check_task")[1]:
            await state.reset_data()
            await self.fsm_task.title.set()
            await message.reply("Введите заголовок задачи:", reply_markup=ReplyKeyboardRemove())

        elif message.text == TASK_BUTTONS.get("check_task")[0]:
            db_data = self.task.to_dict()
            await self.task_db.insert_record_task(data=db_data)
            uuid = await self.task_db.select_uuid_by_title(title=self.task.title)
            await self.task.set_uuid(uuid=uuid)

            # Обновление данных у предыдущей связанной задачи
            if self.task.previous_task != "Нет":
                db_previous_task = await self.task_db.select_task_by_uuid(uuid=int(self.task.previous_task))
                if db_previous_task is not None:
                    old_task = Task()
                    old_task.from_tuple(data=db_previous_task)
                    old_task.next_task = self.task.uuid
                    db_old_task = old_task.to_dict()
                    await self.task_db.update_task_by_uuid(data=db_old_task, uuid=old_task.uuid)
            # Обновление данных у следующей связанной задачи
            if self.task.next_task != "Нет":
                db_next_task = await self.task_db.select_task_by_uuid(uuid=int(self.task.next_task))
                if db_next_task is not None:
                    old_task = Task()
                    old_task.from_tuple(data=db_next_task)
                    old_task.previous_task = self.task.uuid
                    db_old_task = old_task.to_dict()
                    await self.task_db.update_task_by_uuid(data=db_old_task, uuid=old_task.uuid)

            await self.bot.send_message(message.from_user.id, "Задача создана и сохранена\n"
                                                              f"id задачи: {self.task.uuid}",
                                        reply_markup=ReplyKeyboardRemove())
            await state.finish()

            # Оповещение пользователя о его назначении на задачу
            if self.task.executor_id != "Не назначен":
                user_db = UserDb()
                user_id = await user_db.select_user_id_by_username(username=self.task.executor_id)
                await self.bot.send_message(user_id,
                                            f"Вас назначили на задачу {self.task.title} с id = {self.task.uuid}",
                                            reply_markup=ReplyKeyboardRemove())

            kb = self.task_kb.add(GENERAL_BUTTONS)
            await self.bot.send_message(message.from_user.id, 'Главное меню', reply_markup=kb)
        else:
            kb = self.task_kb.add(TASK_BUTTONS.get("check_task"))
            await message.reply('Такой команды нет\n'
                                'Повторите попытку', reply_markup=kb)

    async def closing_task(self, message: Message, state: FSMContext):
        """ Хендлер для команды 'Закрыть задачу' """
        try:
            uuid = int(message.text)
            db_task = await self.task_db.select_task_by_uuid(uuid=uuid)

            if db_task is None:
                await message.reply(f'Задачи с id = {uuid} не существует\n'
                                    'Повторите попытку', reply_markup=ReplyKeyboardRemove())
            else:
                task = Task()
                task.from_tuple(data=db_task)
                if task.status == TASK_STATUS[0]:
                    await message.reply(f'Задача с id = {uuid} еще не назначена\n'
                                        'Прежде чем ее закрывать, необходимо назначить исполнителя и выполнить задачу',
                                        reply_markup=ReplyKeyboardRemove())
                    await state.finish()
                    kb = self.task_kb.add(GENERAL_BUTTONS)
                    await self.bot.send_message(message.from_user.id, 'Главное меню', reply_markup=kb)

                elif task.status == TASK_STATUS[2]:
                    await message.reply(f'Задача с id = {uuid} уже закрыта\n'
                                        'Повторите попытку', reply_markup=ReplyKeyboardRemove())
                else:
                    # обновление данных задачи
                    task.status = TASK_STATUS[2]
                    await task.set_closing_date()
                    db_data = task.to_dict()
                    await self.task_db.update_task_by_uuid(data=db_data, uuid=uuid)

                    # обновление данных рейтинга
                    performance_indicator = PerformanceIndicator()
                    current_performance_indicator = await performance_indicator.calculate_performance_indicator(
                        deadline=task.deadline,
                        closing_date=task.closing_date,
                        complexity=task.complexity)

                    executor_rating_db = ExecutorRatingDb()

                    db_executor_rating = await executor_rating_db.select_performance_indicator_by_executor_id(
                        executor_id=task.executor_id)  # type: Union[Tuple, None]

                    general_performance_indicator = await GeneralPerformanceIndicator. \
                        calculate_general_performance_indicator(
                            db_executor_rating=db_executor_rating,
                            current_performance_indicator=current_performance_indicator)

                    executor_rating = ExecutorRating(current_executor_id=task.executor_id,
                                                     new_performance_indicator=general_performance_indicator)

                    if db_executor_rating is None:
                        db_data_executor_rating = executor_rating.to_dict_for_insert()
                        await executor_rating_db.insert_record_executor(data=db_data_executor_rating)
                    else:
                        db_data_executor_rating = executor_rating.to_dict_for_update()
                        await executor_rating_db.update_performance_indicator_executor(
                            data=db_data_executor_rating)

                    await self.bot.send_message(message.from_user.id, f"Задача с id = {uuid} успешно закрыта",
                                                reply_markup=ReplyKeyboardRemove())
                    await state.finish()

                    kb = self.task_kb.add(GENERAL_BUTTONS)
                    await self.bot.send_message(message.from_user.id, 'Главное меню', reply_markup=kb)
        except ValueError:
            await message.reply('Неверный формат записи id\n'
                                'Повторите попытку')

    def registration(self, dp: Dispatcher):
        """Регистрация хендлеров для задач"""
        dp.register_message_handler(callback=self.tasks, commands=['Задачи'])
        dp.register_message_handler(callback=self.add_task, commands=['Добавить_задачу'],
                                    state=None)
        dp.register_message_handler(callback=self.show_task, commands=['Показать_задачу'],
                                    state=None)
        dp.register_message_handler(callback=self.upd_task, commands=['Редактировать_задачу'],
                                    state=None)
        dp.register_message_handler(callback=self.input_delete_task, commands=['Удалить_задачу'],
                                    state=None)
        dp.register_message_handler(callback=self.input_assign_task, commands=['Назначить_задачу'],
                                    state=None)
        dp.register_message_handler(callback=self.input_closing_task, commands=['Закрыть_задачу'],
                                    state=None)
        dp.register_message_handler(callback=self.cancel, commands=['Отмена'],
                                    state='*')
        dp.register_message_handler(self.cancel, Text(equals='Отмена', ignore_case=True),
                                    state='*')

        # Добавление и обновление задачи
        dp.register_message_handler(callback=self.load_title,
                                    state=self.fsm_task.title)
        dp.register_message_handler(callback=self.load_description,
                                    state=self.fsm_task.description)
        dp.register_message_handler(callback=self.load_complexity,
                                    state=self.fsm_task.complexity)
        dp.register_message_handler(callback=self.load_deadline,
                                    state=self.fsm_task.deadline)

        dp.register_message_handler(callback=self.prepare_previous_task,
                                    state=self.fsm_task.prepare_previous_task)
        dp.register_message_handler(callback=self.load_previous_task,
                                    state=self.fsm_task.previous_task)
        dp.register_message_handler(callback=self.check_previous_task,
                                    state=self.fsm_task.check_previous_task)
        dp.register_message_handler(callback=self.prepare_next_task,
                                    state=self.fsm_task.prepare_next_task)
        dp.register_message_handler(callback=self.load_next_task,
                                    state=self.fsm_task.next_task)
        dp.register_message_handler(callback=self.check_next_task,
                                    state=self.fsm_task.check_next_task)

        dp.register_message_handler(callback=self.load_executor_type,
                                    state=self.fsm_task.executor_type)
        dp.register_message_handler(callback=self.prepare_executor_id,
                                    state=self.fsm_task.prepare_executor_id)
        dp.register_message_handler(callback=self.load_executor_id,
                                    state=self.fsm_task.executor_id)
        dp.register_message_handler(callback=self.check_add_task,
                                    state=self.fsm_task.check_add_task)

        dp.register_message_handler(callback=self.load_upd_uuid,
                                    state=self.fsm_task.upd_uuid)
        dp.register_message_handler(callback=self.check_upd_task,
                                    state=self.fsm_task.check_upd_task)
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

        # Назначение задачи
        dp.register_message_handler(callback=self.assign_task,
                                    state=self.fsm_task.assign_task)
        dp.register_message_handler(callback=self.assign_executor_id,
                                    state=self.fsm_task.assign_executor_id)
        # Закрытие задачи
        dp.register_message_handler(callback=self.closing_task,
                                    state=self.fsm_task.closing_task)
