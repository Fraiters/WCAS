from typing import Dict
from datetime import datetime
from aiogram.types import Message


class Task:
    """Класс Задача"""

    def __init__(self, message: Message):
        self.message = message

        self.title = ...  # type: str
        self.description = ...  # type: str
        self.status = ...  # type: str
        self.priority = ...  # type: str
        self.deadline = ...  # type: datetime
        self.executor_type = ...  # type: str
        self.executor_id = ...  # type: int

    def from_dict(self, data: Dict):
        """Перевод из словаря в данные 'задачи' """
        self.title = data.get("title")
        self.description = data.get("description")
        self.status = data.get("status")
        self.priority = data.get("priority")
        self.deadline = data.get("deadline")
        self.executor_type = data.get("executor_type")

        if data.get("executor_id") is not None:
            self.executor_id = data.get("executor_id")
        else:
            self.executor_id = None

    def to_dict(self):
        """Перевод из данных 'задачи' в словарь"""
        data = {
            "title": self.title,
            "description": self.description,
            "status": self.status,
            "priority": self.priority,
            "deadline": self.deadline,
            "executor_type": self.executor_type,
            "executor_id": self.executor_id
        }
        return data

    async def print_info(self):
        """Вывод данных о задачи в сообщении"""

        if self.executor_id is None:
            self.executor_id = "Не назначен"

        await self.message.reply(f"Название задачи: {self.title}\n\n"
                                 f"Описание: \n{self.description}\n"
                                 f"Готовность: {self.status}\n"
                                 f"Приоритет: {self.priority}\n"
                                 f"Срок выполнения: {self.deadline}\n"
                                 f"Тип исполнителя: {self.executor_type}\n"
                                 f"Исполнитель: {self.executor_id}\n")


# Статус задачи
TASK_STATUS = ["ToDo", "Doing", "Done"]
