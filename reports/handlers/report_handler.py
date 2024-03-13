from aiogram import Bot, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.types import Message
from reports.keyboards.report_kb import ReportKb
from aiogram.types import ReplyKeyboardRemove
from settings import REPORT_BUTTONS
from models.report import Report


class FsmReport(StatesGroup):
    """Класс машины состояний для отчетов"""
    id_related_task = State()
    description = State()
    check_report = State()


class ReportHandler:
    """Класс хендлеров для отчетов """

    def __init__(self, bot: Bot):
        self.bot = bot
        self.report_kb = ReportKb()
        self.fsm_report = FsmReport()
        self.report = ...

    async def expenses(self, message: Message):
        """Хендлер для команды 'Отчеты' """
        kb = self.report_kb.add(REPORT_BUTTONS.get("add_report"))
        await self.bot.send_message(message.from_user.id, 'Чтобы добавить отчет нажмите на "Добавить отчет"',
                                    reply_markup=kb)

    async def add_report(self, message: Message):
        """Хендлер для команды 'Добавить отчет' (Вход в машину состояний)"""
        await self.fsm_report.id_related_task.set()
        await message.reply("Введите id связанной задачи", reply_markup=ReplyKeyboardRemove())

    async def cancel(self, message: Message, state: FSMContext):
        """Выход из машины состояний"""
        current_state = await state.get_state()
        if current_state is None:
            return
        await state.finish()
        await message.reply('OK')

    async def load_id_related_task(self, message: Message, state: FSMContext):
        """Загрузка id связанной задачи"""
        try:
            async with state.proxy() as data:
                data['id_related_task'] = int(message.text)
                # Добавить название связанной задачи с помощью поиска по id
                # data['title_related_task'] =
            await self.fsm_report.next()
            await message.reply('Введите содержание отчета', reply_markup=ReplyKeyboardRemove())
        except Exception:
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
            await self.bot.send_message(message.from_user.id, "Отчет составлен и сохранен",
                                        reply_markup=ReplyKeyboardRemove())
            await state.finish()
        else:
            kb = self.report_kb.add(REPORT_BUTTONS.get("check_report"))
            await message.reply('Такой команды нет\n'
                                'Повторите попытку', reply_markup=kb)

    def registration(self, dp: Dispatcher):
        """Регистрация хендлеров для отчетов"""
        dp.register_message_handler(callback=self.expenses, commands=['Отчеты'])
        dp.register_message_handler(callback=self.add_report, commands=['Добавить_отчет'],
                                    state=None)
        dp.register_message_handler(callback=self.cancel, commands=['Отмена'],
                                    state='*')
        dp.register_message_handler(self.cancel, Text(equals='Отмена', ignore_case=True),
                                    state='*')
        dp.register_message_handler(callback=self.load_id_related_task,
                                    state=self.fsm_report.id_related_task)
        dp.register_message_handler(callback=self.load_description,
                                    state=self.fsm_report.description)
        dp.register_message_handler(callback=self.check_report,
                                    state=self.fsm_report.check_report)
