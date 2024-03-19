from typing import List, Tuple
from aiogram import Bot, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.types import Message
from reports.keyboards.report_kb import ReportKb
from aiogram.types import ReplyKeyboardRemove
from settings import REPORT_BUTTONS, GENERAL_BUTTONS
from models.report import Report
from reports.db.report_db import ReportBaseDb
from tasks.db.task_db import TaskBaseDb


class FsmReport(StatesGroup):
    """ Класс машины состояний для отчетов """
    title = State()
    id_related_task = State()
    description = State()
    check_report = State()

    show_by_user_id = State()
    show_by_uuid = State()


class ReportHandler:
    """ Класс хендлеров для отчетов """

    def __init__(self, bot: Bot, db_name: str):
        self.bot = bot
        self.report_kb = ReportKb()
        self.fsm_report = FsmReport()
        self.task_db = TaskBaseDb(db_name=db_name)
        self.report_db = ReportBaseDb(db_name=db_name)
        self.report = ...  # type: Report

    # Уровень клавиатуры 1
    # /Добавить отчет, /Показать отчет
    async def reports(self, message: Message):
        """ Хендлер для команды 'Отчеты' """
        kb = self.report_kb.add(REPORT_BUTTONS.get("report"))
        await self.bot.send_message(message.from_user.id, 'Чтобы добавить отчет нажмите на "Добавить отчет"\n'
                                                          'Чтобы посмотреть отчеты нажмите на "Показать"\n'
                                                          'Для отмены введите команду "/Отмена"', reply_markup=kb)

    # Уровень клавиатуры 2
    # Добавить отчет:
    async def add_report(self, message: Message):
        """ Хендлер для команды 'Добавить отчет' (Вход в машину состояний) """

        await self.fsm_report.title.set()
        await message.reply("Введите название отчета", reply_markup=ReplyKeyboardRemove())

    # Уровень клавиатуры 2
    # Показать отчеты:
    # /Показать_все_отчеты, /Показать_отчеты_по_id_исполнителя, /Показать_отчет_по_уникальному_id
    async def show_report(self, message: Message):
        """ Хендлер для команды 'Показать отчет' """
        kb = self.report_kb.add(REPORT_BUTTONS.get("show_reports"))
        await message.reply("Выберите параметры просмотра", reply_markup=kb)

    async def cancel(self, message: Message, state: FSMContext):
        """Выход из машины состояний"""
        current_state = await state.get_state()
        if current_state is None:
            return
        await state.finish()
        kb = self.report_kb.add(GENERAL_BUTTONS)
        await self.bot.send_message(message.from_user.id, 'Главное меню', reply_markup=kb)

    async def show_all_reports(self, message: Message):
        """ Хендлер для команды 'Показать все отчеты' """
        db_reports = await self.report_db.select_all_reports()  # type: List[Tuple]

        reports = []  # type: List[Report]

        for uuid, title in db_reports:
            report = Report(message=message)
            report.uuid = uuid
            report.title = title
            reports.append(report)

        for report in reports:
            await message.answer(f"id отчета: {report.uuid}\n"
                                 f"Название отчета: {report.title}\n", reply_markup=ReplyKeyboardRemove())

        kb = self.report_kb.add(GENERAL_BUTTONS)
        await self.bot.send_message(message.from_user.id, 'Главное меню', reply_markup=kb)

    async def input_user_id(self, message: Message):
        """Хендлер для ввода user_id для команды 'Показать отчет по id исполнителя' """

        await self.fsm_report.show_by_user_id.set()
        await self.bot.send_message(message.from_user.id, "Введите id исполнителя (через @)",
                                    reply_markup=ReplyKeyboardRemove())

    async def show_report_by_user_id(self, message: Message, state: FSMContext):
        """Хендлер для команды 'Показать отчет по id исполнителя' """
        user_id = message.text
        db_reports = await self.report_db.select_report_by_user_id(user_id=user_id)
        reports = []  # type: List[Report]

        if db_reports == []:
            await message.reply(f'Отчеты с id исполнителя = {user_id} не найдены'
                                'Повторите попытку', reply_markup=ReplyKeyboardRemove())
        else:
            for uuid, title, title_related_task, id_related_task, description, author, date, time in db_reports:
                report = Report(message=message)
                report.uuid = uuid
                report.title = title
                report.title_related_task = title_related_task
                report.id_related_task = id_related_task
                report.description = description
                report.author = author
                report.date = date
                report.time = time
                reports.append(report)

            await state.finish()
            for report in reports:
                await message.answer(f"id отчета: {report.uuid}\n"
                                     f"Название отчета: {report.title}\n"
                                     f"Отчет по задаче: {report.title_related_task}\n"
                                     f"id связанной задачи: {report.id_related_task}\n"
                                     f"Содержание: \n{report.description}\n\n"
                                     f"Автор: {report.author}\n"
                                     f"Дата составления отчета: {report.date}\n"
                                     f"Время составления отчета: {report.time}\n", reply_markup=ReplyKeyboardRemove())

            kb = self.report_kb.add(GENERAL_BUTTONS)
            await self.bot.send_message(message.from_user.id, 'Главное меню', reply_markup=kb)

    async def input_uuid(self, message: Message):
        """Хендлер для ввода uuid для команды 'Показать отчет по уникальному id' """

        await self.fsm_report.show_by_uuid.set()
        await self.bot.send_message(message.from_user.id, "Введите уникальный id отчета",
                                    reply_markup=ReplyKeyboardRemove())

    async def show_report_by_uuid(self, message: Message, state: FSMContext):
        """Хендлер для команды 'Показать отчет по уникальному id' """
        try:
            uuid = int(message.text)
            db_report = await self.report_db.select_report_by_uuid(uuid=uuid)
            if db_report is None:
                await message.reply(f'Отчета с id = {uuid} не существует\n'
                                    'Повторите попытку')
            else:
                report = Report(message=message)
                for uuid, title, title_related_task, id_related_task, description, author, date, time in [db_report]:
                    report.uuid = uuid
                    report.title = title
                    report.title_related_task = title_related_task
                    report.id_related_task = id_related_task
                    report.description = description
                    report.author = author
                    report.date = date
                    report.time = time
                await state.finish()
                await message.answer(f"id отчета: {report.uuid}\n"
                                     f"Название отчета: {report.title}\n"
                                     f"Отчет по задаче: {report.title_related_task}\n"
                                     f"id связанной задачи: {report.id_related_task}\n"
                                     f"Содержание: \n{report.description}\n\n"
                                     f"Автор: {report.author}\n"
                                     f"Дата составления отчета: {report.date}\n"
                                     f"Время составления отчета: {report.time}\n", reply_markup=ReplyKeyboardRemove())

                kb = self.report_kb.add(GENERAL_BUTTONS)
                await self.bot.send_message(message.from_user.id, 'Главное меню', reply_markup=kb)

        except ValueError:
            await message.reply('Неверный формат записи id\n'
                                'Повторите попытку')

    async def load_title(self, message: Message, state: FSMContext):
        """Загрузка заголовка отчета"""
        async with state.proxy() as data:
            data['title'] = message.text
            # TO DO: добавить отловку исключения на создание не уникального title
        await self.fsm_report.next()
        await message.reply("Введите id связанной задачи", reply_markup=ReplyKeyboardRemove())

    async def load_id_related_task(self, message: Message, state: FSMContext):
        """Загрузка id связанной задачи"""
        try:
            async with state.proxy() as data:
                data['id_related_task'] = int(message.text)
                # Добавление названия связанной задачи с помощью поиска по id
                title_related_task = await self.task_db.select_title_by_uuid(uuid=data['id_related_task'])
                if title_related_task is None:
                    await message.reply(f'Задачи с id = {data["id_related_task"]} не существует\n'
                                        'Повторите попытку')
                data['title_related_task'] = title_related_task[0]
            await self.fsm_report.next()
            await message.reply('Введите содержание отчета', reply_markup=ReplyKeyboardRemove())
        except ValueError:
            await message.reply('Неверный формат записи id\n'
                                'Повторите попытку')

    async def load_description(self, message: Message, state: FSMContext):
        """Загрузка содержания"""
        async with state.proxy() as data:
            data['description'] = message.text

        async with state.proxy() as data:
            self.report = Report(message=message)
            self.report.from_dict(data=data)
            await self.report.print_info()

        await self.fsm_report.check_report.set()
        kb = self.report_kb.add(REPORT_BUTTONS.get("check_report"))
        await self.bot.send_message(message.from_user.id, "Все верно?", reply_markup=kb)

    async def check_report(self, message: Message, state: FSMContext):
        """Проверка отчета"""
        if message.text == REPORT_BUTTONS.get("check_report")[1]:
            await self.fsm_report.id_related_task.set()
            await self.bot.send_message(message.from_user.id, "Введите id связанной задачи",
                                        reply_markup=ReplyKeyboardRemove())
        elif message.text == REPORT_BUTTONS.get("check_report")[0]:
            db_data = self.report.to_dict()
            await self.report_db.insert_record_report(data=db_data)
            uuid = await self.report_db.select_uuid_by_title(title=self.report.title)
            await self.report.set_uuid(uuid=uuid)
            await self.bot.send_message(message.from_user.id, "Отчет составлен и сохранен\n"
                                                              f"id отчета: {self.report.uuid}",
                                        reply_markup=ReplyKeyboardRemove())
            await state.finish()
            kb = self.report_kb.add(GENERAL_BUTTONS)
            await self.bot.send_message(message.from_user.id, 'Главное меню', reply_markup=kb)
        else:
            kb = self.report_kb.add(REPORT_BUTTONS.get("check_report"))
            await message.reply('Такой команды нет\n'
                                'Повторите попытку', reply_markup=kb)

    def registration(self, dp: Dispatcher):
        """Регистрация хендлеров для отчетов"""
        dp.register_message_handler(callback=self.reports, commands=['Отчеты'])
        dp.register_message_handler(callback=self.add_report, commands=['Добавить_отчет'],
                                    state=None)
        dp.register_message_handler(callback=self.show_report, commands=['Показать_отчет'],
                                    state=None)
        dp.register_message_handler(callback=self.cancel, commands=['Отмена'],
                                    state='*')
        dp.register_message_handler(self.cancel, Text(equals='Отмена', ignore_case=True),
                                    state='*')
        # Создание отчета
        dp.register_message_handler(callback=self.load_title,
                                    state=self.fsm_report.title)
        dp.register_message_handler(callback=self.load_id_related_task,
                                    state=self.fsm_report.id_related_task)
        dp.register_message_handler(callback=self.load_description,
                                    state=self.fsm_report.description)
        dp.register_message_handler(callback=self.check_report,
                                    state=self.fsm_report.check_report)
        # Просмотр отчета
        dp.register_message_handler(callback=self.show_all_reports, commands=['Показать_все_отчеты'],
                                    state=None)
        dp.register_message_handler(callback=self.input_user_id, commands=['Показать_отчеты_по_id_исполнителя'],
                                    state=None)
        dp.register_message_handler(callback=self.input_uuid, commands=['Показать_отчет_по_уникальному_id'],
                                    state=None)
        dp.register_message_handler(callback=self.show_report_by_user_id,
                                    state=self.fsm_report.show_by_user_id)
        dp.register_message_handler(callback=self.show_report_by_uuid,
                                    state=self.fsm_report.show_by_uuid)
