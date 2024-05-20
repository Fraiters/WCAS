from typing import Dict, Union, Tuple
from aiogram.types import Message
from utils.utils import get_current_date


class Task:
    """Класс Задача"""

    def __init__(self):

        self.uuid = None  # type: Union[int, None]
        self.title = ...  # type: str
        self.description = ...  # type: str
        self.status = ...  # type: str
        self.complexity = ...  # type: str
        self.deadline = ...  # type: str
        self.closing_date = ...  # type: str
        self.previous_task = ...  # type: str
        self.next_task = ...  # type: str
        self.executor_type = ...  # type: str
        self.executor_id = ...  # type: str

    def from_dict(self, data: Dict):
        """Перевод из словаря в данные 'задачи' """
        self.title = data.get("title")
        self.description = data.get("description")
        self.status = data.get("status")
        self.complexity = data.get("complexity")
        self.deadline = data.get("deadline")
        self.closing_date = data.get("closing_date")
        self.previous_task = data.get("previous_task")
        self.next_task = data.get("next_task")

        self.executor_type = data.get("executor_type")
        self.executor_id = data.get("executor_id")

    def from_tuple(self, data: Tuple):
        """Перевод из кортежа в данные 'задачи' """
        for uuid, title, description, status, complexity, deadline, closing_date, previous_task, next_task,\
                executor_type, executor_id in [data]:
            self.uuid = uuid
            self.title = title
            self.description = description
            self.status = status
            self.complexity = complexity
            self.deadline = deadline
            self.closing_date = closing_date
            self.previous_task = previous_task
            self.next_task = next_task
            self.executor_type = executor_type
            self.executor_id = executor_id

    def to_dict(self):
        """Перевод из данных 'задачи' в словарь"""
        data = {
            "title": self.title,
            "description": self.description,
            "status": self.status,
            "complexity": self.complexity,
            "deadline": self.deadline,
            "closing_date": self.closing_date,
            "previous_task": self.previous_task,
            "next_task": self.next_task,
            "executor_type": self.executor_type,
            "executor_id": self.executor_id
        }
        return data

    async def set_uuid(self, uuid: int):
        self.uuid = uuid

    async def set_closing_date(self):
        self.closing_date = str(get_current_date())

    async def print_info(self, message: Message):
        """Вывод всех данных о задачи в сообщении"""

        if self.executor_id is None:
            self.executor_id = "Не назначен"

        if self.previous_task is None:
            self.previous_task = "Нет"

        if self.next_task is None:
            self.next_task = "Нет"

        if self.closing_date is None:
            self.closing_date = "Не выполнена"

        await message.reply(f"Название задачи: {self.title}\n\n"
                            f"Описание: \n{self.description}\n"
                            f"Готовность: {self.status}\n"
                            f"Сложность: {self.complexity}\n"
                            f"Срок выполнения: {self.deadline}\n"
                            f"Тип исполнителя: {self.executor_type}\n"
                            f"Исполнитель: @{self.executor_id}\n\n"
                            f"Предыдущая связанная задача (id): {self.previous_task}\n"
                            f"Следующая связанная задача (id): {self.next_task}\n"
                            f"Дата закрытия задачи: {self.closing_date}\n")


# Статус задачи
TASK_STATUS = ["ToDo", "Doing", "Done"]
