from typing import Dict, Union, Tuple
from datetime import datetime
from aiogram.types import Message, ReplyKeyboardRemove


class Report:
    """Класс Отчета"""

    def __init__(self):
        self.uuid = None  # type: Union[int, None]
        self.title = ...  # type: str
        self.title_related_task = ...  # type: str
        self.id_related_task = ...  # type: int
        self.description = ...  # type: str
        self.author = ...  # type: str
        self.date = str(datetime.now().date().strftime('%d.%m.%Y'))
        self.time = self.get_time()

    def from_tuple(self, data: Tuple):
        """Перевод из кортежа в данные 'задачи' """
        for uuid, title, title_related_task, id_related_task, description, author, date, time in [data]:
            self.uuid = uuid
            self.title = title
            self.title_related_task = title_related_task
            self.id_related_task = id_related_task
            self.description = description
            self.author = author
            self.date = date
            self.time = time

    def from_dict(self, data: Dict):
        """Перевод из словаря в данные 'отчета' """
        self.uuid = data.get("uuid")
        self.title = data.get("title")
        self.title_related_task = data.get("title_related_task")
        self.id_related_task = data.get("id_related_task")
        self.description = str(data.get("description"))

    def to_dict(self):
        """Перевод из данных 'отчета' в словарь"""
        data = {
            "title": self.title,
            "title_related_task": self.title_related_task,
            "id_related_task": self.id_related_task,
            "description": self.description,
            "author": self.author,
            "date": self.date,
            "time": self.time,
        }
        return data

    async def set_uuid(self, uuid: int):
        self.uuid = uuid

    async def set_author(self, message: Message):
        self.author = message.from_user.username.lower()

    async def print_info(self, message: Message):
        """Вывод данных об отчете в сообщении"""
        await message.reply(f"Название отчета: {self.title}\n"
                            f"Отчет по задаче: {self.title_related_task}\n"
                            f"id связанной задачи: {self.id_related_task}\n"
                            f"Содержание: \n{self.description}\n\n"
                            f"Автор: @{self.author}\n"
                            f"Дата составления отчета: {self.date}\n"
                            f"Время составления отчета: {self.time}\n", reply_markup=ReplyKeyboardRemove())

    def get_time(self):
        time = datetime.now().time()
        hours = str(time.hour)
        minutes = str(time.minute)
        formatted_time = ":".join([hours, minutes])
        return formatted_time
