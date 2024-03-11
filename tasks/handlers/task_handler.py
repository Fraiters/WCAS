from aiogram import Bot, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.types import Message
from aiogram.types import ReplyKeyboardRemove
from settings import TASK_BUTTONS
from models.task import Task, TASK_STATUS
from tasks.keyboards.task_kb import TaskKb
from utils.utils import is_datetime


class FsmTask(StatesGroup):
    """Класс машины состояний для задач"""
    title = State()
    description = State()
    priority = State()
    deadline = State()
    executor_type = State()
    prepare_executor_id = State()
    executor_id = State()
    check_task = State()


class TaskHandler:
    """Класс хендлеров для задач """

    def __init__(self, bot: Bot):
        self.bot = bot
        self.task_kb = TaskKb()
        self.fsm_task = FsmTask()
        self.task = ...  # type: Task

    async def tasks(self, message: Message):
        """Хендлер для команды 'Задачи' """
        kb = self.task_kb.add(TASK_BUTTONS.get("add_task"))
        await self.bot.send_message(message.from_user.id, 'Чтобы добавить задачу нажмите на "/Добавить_задачу" \n'
                                                          'для отмены введите команду "/Отмена"',
                                    reply_markup=kb)

    async def add_task(self, message: Message):
        """Хендлер для команды 'Добавить задачу' (Вход в машину состояний)"""
        await self.fsm_task.title.set()
        await message.reply("Введите заголовок задачи", reply_markup=ReplyKeyboardRemove())

    async def cancel(self, message: Message, state: FSMContext):
        """Выход из машины состояний"""
        current_state = await state.get_state()
        if current_state is None:
            return
        await state.finish()
        await message.reply('OK')

    async def load_title(self, message: Message, state: FSMContext):
        """Загрузка заголовка задачи"""
        async with state.proxy() as data:
            data['title'] = message.text
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
        if message.text == "/Нет":
            async with state.proxy() as data:
                data['status'] = TASK_STATUS[0]
                self.task = Task(message=message)
                self.task.from_dict(data=data)
                await self.task.print_info()

            await self.fsm_task.check_task.set()
            kb = self.task_kb.add(TASK_BUTTONS.get("check_task"))
            await self.bot.send_message(message.from_user.id, "Все верно?", reply_markup=kb)

        elif message.text == "/Да":
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
            await self.bot.send_message(message.from_user.id, "Задача создана и сохранена",
                                        reply_markup=ReplyKeyboardRemove())
            await state.finish()

    def registration(self, dp: Dispatcher):
        """Регистрация хендлеров для задач"""
        dp.register_message_handler(callback=self.tasks, commands=['Задачи'])
        dp.register_message_handler(callback=self.add_task, commands=['Добавить_задачу'],
                                    state=None)
        dp.register_message_handler(callback=self.cancel, commands=['Отмена'],
                                    state='*')
        dp.register_message_handler(self.cancel, Text(equals='Отмена', ignore_case=True),
                                    state='*')
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
